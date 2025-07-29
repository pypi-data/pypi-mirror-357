# Copyright (c) 2025, Wentao Guo, Ted Zadouri, Tri Dao.

import math
import operator

import torch

import cuda.bindings.driver as cuda

import cutlass
import cutlass.cute as cute
from cutlass.cute.runtime import from_dlpack

import quack.utils as utils


@cute.kernel
def rmsnorm_kernel(
    mX: cute.Tensor,
    mW: cute.Tensor,
    mO: cute.Tensor,
    mRstd: cute.Tensor,
    eps: cute.Float32,
    tv_layout: cute.Layout,
    tiler_mn: cute.Shape,
    cluster_n: cutlass.Constexpr = 1,
    reload_from: cutlass.Constexpr = None,
    delay_w_load: cutlass.Constexpr = False,
):
    tidx, _, _ = cute.arch.thread_idx()
    bidx, cluster_y, _ = cute.arch.block_idx()

    smem = cutlass.utils.SmemAllocator()
    sX = smem.allocate_tensor(mX.element_type, cute.make_ordered_layout(tiler_mn, order=(1, 0)), byte_alignment=16)
    num_warps = cute.size(tv_layout, mode=[0]) // cute.arch.WARP_SIZE
    warps_per_row = utils.max_constexpr(tv_layout.shape[0][0] // cute.arch.WARP_SIZE, 1)
    reduction_buffer_layout = cute.make_ordered_layout(
        (num_warps // warps_per_row, (warps_per_row, cluster_n)),
        order=(1, 0)
    )
    reduction_buffer = smem.allocate_tensor(cutlass.Float32, reduction_buffer_layout, byte_alignment=4)
    if cutlass.const_expr(cluster_n > 1):
        mbar_ptr = smem.allocate(cutlass.Int64.width // 8, byte_alignment=8)
    else:
        mbar_ptr = None

    shape = mX.shape
    idX = cute.make_identity_tensor(shape)
    # slice for CTAs
    gX, gO, gRstd, cX = [
        cute.local_tile(mT, tiler_mn, (bidx, 0 if cluster_n == 1 else cluster_y))
        for mT in (mX, mO, mRstd, idX)
    ]
    gW = cute.local_tile(mW, tiler_mn, (0, 0 if cluster_n == 1 else cluster_y))

    # declare the atoms which will be used later for memory copy
    copy_atom_load_X = cute.make_copy_atom(cute.nvgpu.CopyUniversalOp(), mX.element_type, num_bits_per_copy=128)
    copy_atom_load_X_async = cute.make_copy_atom(cute.nvgpu.cpasync.CopyG2SOp(), mX.element_type, num_bits_per_copy=128)
    copy_atom_load_W = cute.make_copy_atom(cute.nvgpu.CopyUniversalOp(), mW.element_type, num_bits_per_copy=128)
    copy_atom_store_O = cute.make_copy_atom(cute.nvgpu.CopyUniversalOp(), mO.element_type, num_bits_per_copy=128)

    thr_copy_X = cute.make_tiled_copy(copy_atom_load_X_async, tv_layout, tiler_mn).get_slice(tidx)
    thr_copy_W = cute.make_tiled_copy(copy_atom_load_W, tv_layout, tiler_mn).get_slice(tidx)
    thr_copy_O = cute.make_tiled_copy(copy_atom_store_O, tv_layout, tiler_mn).get_slice(tidx)

    tWgW = thr_copy_W.partition_S(gW)
    tXgX = thr_copy_X.partition_S(gX)
    tXsX = thr_copy_X.partition_D(sX)
    tXgO, tXrRstd = [thr_copy_O.partition_D(gT) for gT in (gO, gRstd)]
    tXcX = thr_copy_X.partition_S(cX)[(0, None), None, None]

    # allocate fragments for gmem->rmem
    tWrW = cute.make_fragment_like(tWgW)
    tXrW = thr_copy_X.retile(tWrW)
    tXrX, tXrO = [cute.make_fragment_like(thr) for thr in (tXgX, tXgO)]

    if cluster_n > 1:
        if tidx == 0:
            cute.arch.mbarrier_init_arrive_cnt(mbar_ptr, 1)
        cute.arch.mbarrier_init_fence()
        if tidx == 0:
            cute.arch.mbarrier_init_tx_bytes(mbar_ptr, num_warps * cluster_n * cutlass.Float32.width // 8)
        # Cluster arrive after barrier init
        cute.arch.cluster_arrive_relaxed()

    tXpX = utils.predicate_k(thr_copy_X.partition_S(cX), limit=shape[1])
    row = tXcX[0][0]
    if row < shape[0]:
        cute.copy(copy_atom_load_X_async, tXgX, tXsX, pred=tXpX)
    cute.arch.cp_async_commit_group()

    tWpW = utils.predicate_k(thr_copy_W.partition_S(cX), limit=shape[1])
    if not delay_w_load:
        cute.copy(copy_atom_load_W, tWgW, tWrW, pred=tWpW)

    cute.arch.cp_async_wait_group(0)
    cute.autovec_copy(tXsX, tXrX)
    x = tXrX.load().to(cute.Float32)
    threads_per_row = tv_layout.shape[0][0]
    sum_sq_x = utils.row_reduce(
        x * x,
        cute.ReductionOp.ADD,
        threads_per_row,
        reduction_buffer,
        mbar_ptr,
        init_val=0.0,
        hook_fn=cute.arch.cluster_wait if cutlass.const_expr(cluster_n > 1) else None
    )
    rstd = utils.rsqrt(sum_sq_x / shape[1] + eps)
    # Only the thread corresponding to column 0 writes out the rstd to gmem
    if tXcX[0][1] == 0 and row < shape[0] and (cluster_n == 1 or cute.arch.block_idx_in_cluster() == 0):
        tXrRstd[0] = rstd
    if delay_w_load:
        cute.copy(copy_atom_load_W, tWgW, tWrW, pred=tWpW)
    if reload_from == "smem":
        cute.autovec_copy(tXsX, tXrX)
        x = tXrX.load().to(cute.Float32)
    elif reload_from == "gmem":
        cute.copy(copy_atom_load_X, tXgX, tXrX, pred=tXpX)
        x = tXrX.load().to(cute.Float32)
    x_hat = x * rstd
    w = tXrW.load().to(cute.Float32)
    y = x_hat * w
    tXrO.store(y.to(tXrO.element_type))
    tOpO = utils.predicate_k(thr_copy_O.partition_S(cX), limit=shape[1])
    if row < shape[0]:
        cute.copy(copy_atom_store_O, tXrO, tXgO, pred=tOpO)


@cute.jit
def rmsnorm_interface(
    mX: cute.Tensor,
    mW: cute.Tensor,
    mO: cute.Tensor,
    mRstd: cute.Tensor,
    stream: cuda.CUstream,
    N: cutlass.Constexpr,
    eps: cutlass.Float32 = 1e-6,
    copy_bits: cutlass.Constexpr = 128
):
    # new_shape = (mX_.shape[0], cute.assume(mX_.shape[1], 128))
    # breakpoint()
    # mX = cute.make_tensor(mX_.iterator, cute.make_layout(new_shape, stride=mX_.stride))
    vecsize = copy_bits // mX.element_type.width
    assert N % vecsize == 0, f"Input N {N} is not divisible by vector size {vecsize}"
    num_threads = 128 if N <= 16384 else 256
    num_warps = num_threads // cute.arch.WARP_SIZE
    assert num_threads % cute.arch.WARP_SIZE == 0
    threads_per_row = 8 if N <= 64 else (16 if N <= 128 else (32 if N <= 3072 else (64 if N <= 6144 else (128 if N <= 16384 else 256))))
    # cluster_n = 4 is faster and cluster_n = 2 for N=64k for some reason
    # Similarly cluster_n = 8 is faster for N=128k
    if cutlass.const_expr(mX.element_type.width == 16):
        cluster_n = 1 if N <= 16 * 1024 else (2 if N <= 32 * 1024 else (4 if N <= 64 * 1024 else (8 if N <= 128 * 1024 else 16)))
    else:  # fp32
        cluster_n = 1 if N <= 32 * 1024 else (2 if N <= 64 * 1024 else (4 if N <= 128 * 1024 else (8 if N <= 256 * 1024 else 16)))

    num_blocks_N = cute.ceil_div(N // vecsize, threads_per_row * cluster_n)
    cols_per_block = num_threads // threads_per_row
    tiler_mn = (cols_per_block, vecsize * num_blocks_N * threads_per_row)  # This rounds up N
    tv_layout = cute.make_layout(
        ((threads_per_row, cols_per_block), (vecsize, num_blocks_N)),
        stride=((vecsize * cols_per_block, 1), (cols_per_block, cols_per_block * vecsize * threads_per_row))
    )

    mW_expanded_layout = cute.prepend(mW.layout, cute.make_layout((tiler_mn[0],), stride=(0,)))
    mW_expanded = cute.make_tensor(mW.iterator, mW_expanded_layout)
    mRstd_expanded_layout = cute.append(mRstd.layout, cute.make_layout((N,), stride=(0,)))
    mRstd_expanded = cute.make_tensor(mRstd.iterator, mRstd_expanded_layout)

    # reload_from = None if N <= 16384 else ("smem" if N <= 32768 else "gmem")
    reload_from = None if N <= 16384 else "smem"
    # delay_w_load = N > 64 * 1024
    delay_w_load = False
    N_rounded = tiler_mn[1]
    rmsnorm_kernel(mX, mW_expanded, mO, mRstd_expanded, eps, tv_layout, tiler_mn, cluster_n, reload_from).launch(
        grid=[cute.ceil_div(mX.shape[0], tiler_mn[0]), cluster_n, 1],
        block=[cute.size(tv_layout, mode=[0]), 1, 1],
        # Launching with cluster=[1, 1, 1] instead of None slows down the kernel by ~8us
        cluster=[1, cluster_n, 1] if cluster_n > 1 else None,
        smem=cute.size_in_bytes(mX.element_type, cute.make_layout(tiler_mn)) + num_warps * cluster_n * (cutlass.Float32.width // 8) + (cutlass.Int64.width // 8),
        stream=stream,
    )


torch2cute_dtype_map = {
    torch.float16: cutlass.Float16,
    torch.bfloat16: cutlass.BFloat16,
    torch.float32: cutlass.Float32,
}


def rmsnorm(
    x: torch.Tensor,
    weight: torch.Tensor,
    eps: float = 1e-6,
    return_rstd: bool = False,
) -> torch.Tensor:
    """RMSNorm forward pass.

    Args:
        x: Input tensor of shape (M, N)
        weight: Weight tensor of shape (N,)
        eps: Small value for numerical stability
        return_rstd: Whether to return the reciprocal standard deviation

    Returns:
        Normalized output tensor of same shape as x
        If return_rstd is True, also returns rstd tensor of shape (M,)
    """
    assert x.dim() == 2, "Input must be 2D"
    assert weight.dim() == 1, "Weight must be 1D"
    assert x.shape[-1] == weight.shape[0], "Last dimension of input must match weight dimension"
    assert x.is_cuda and weight.is_cuda, "Tensors must be on CUDA device"
    assert x.dtype in [torch.float16, torch.bfloat16, torch.float32], "Unsupported dtype"
    assert weight.dtype == torch.float32, "Weight must be float32"
    M, N = x.shape
    device = x.device
    out = torch.empty_like(x)
    rstd = torch.empty(M, device=device, dtype=torch.float32)
    dtype = torch2cute_dtype_map[x.dtype]
    convert_from_dlpack = lambda x: (
        from_dlpack(x.detach(), assumed_align=16)
        .mark_compact_shape_dynamic(mode=0, stride_order=(0, 1))
    )
    x_tensor, out_tensor = [
        # utils.convert_from_dlpack(t, leading_dim=t.ndim - 1, divisibility=128 // dtype.width)
        convert_from_dlpack(t)
        for t in (x, out)
    ]
    weight_tensor = utils.convert_from_dlpack(weight.detach(), leading_dim=0, divisibility=128 // cutlass.Float32.width)
    rstd_tensor = from_dlpack(rstd.detach(), assumed_align=4).mark_layout_dynamic(leading_dim=0)
    current_stream = cuda.CUstream(torch.cuda.current_stream().cuda_stream)
    compile_key = (dtype, N)
    if compile_key not in rmsnorm.compile_cache:
        rmsnorm.compile_cache[compile_key] = cute.compile(
            rmsnorm_interface, x_tensor, weight_tensor, out_tensor, rstd_tensor, current_stream, N
        )
    rmsnorm.compile_cache[compile_key](
        x_tensor, weight_tensor, out_tensor, rstd_tensor, current_stream, eps
    )
    return (out, rstd) if return_rstd else out


rmsnorm.compile_cache = {}


def rmsnorm_ref(x, w, eps=1e-6):
    x_f32 = x.float()
    return (x_f32 / (torch.sqrt(torch.mean(x_f32 * x_f32, dim=-1, keepdim=True) + eps)) * w).to(x.dtype)


def rstd_ref(x, eps=1e-6):
    x_f32 = x.float()
    return 1.0 / torch.sqrt(torch.mean(x_f32 * x_f32, dim=-1) + eps)
