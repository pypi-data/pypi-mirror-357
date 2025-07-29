# Copyright (c) 2025, Wentao Guo, Ted Zadouri, Tri Dao.

import operator
import math
from typing import Type, Callable, Optional

import cutlass
import cutlass.cute as cute

from cutlass.cutlass_dsl import T, dsl_user_op
from cutlass._mlir.dialects import nvvm, llvm
from cutlass.cute.runtime import from_dlpack


def convert_from_dlpack(x, leading_dim, alignment=16, divisibility=1) -> cute.Tensor:
    return (
        from_dlpack(x, assumed_align=alignment)
        .mark_layout_dynamic(leading_dim=leading_dim)
        .mark_compact_shape_dynamic(
            mode=leading_dim, stride_order=x.dim_order(), divisibility=divisibility
        )
    )


@cute.jit
def max_constexpr(
    a: cutlass.Constexpr[cute.Numeric], b: cutlass.Constexpr[cute.Numeric]
) -> cutlass.Constexpr[cute.Numeric]:
    return a if a > b else b


@cute.jit
def min_constexpr(
    a: cutlass.Constexpr[cute.Numeric], b: cutlass.Constexpr[cute.Numeric]
) -> cutlass.Constexpr[cute.Numeric]:
    return a if a < b else b


def warp_reduce(
    val: cute.TensorSSA | cute.Numeric,
    op: Callable,
    width: cutlass.Constexpr[int] = cute.arch.WARP_SIZE
) -> cute.TensorSSA | cute.Numeric:
    if isinstance(val, cute.TensorSSA):
        res = cute.make_fragment(val.shape, val.dtype)
        res.store(val)
        for i in range(cute.size(val.shape)):
            res[i] = warp_reduce(res[i], op, width)
        return res.load()
    else:
        for i in range(int(math.log2(width))):
            val = op(val, cute.arch.shuffle_sync_bfly(val, offset=1 << i))
    return val


@cute.jit
def block_reduce(val: cute.Numeric, op: Callable, reduction_buffer: cute.Tensor, init_val: cute.Numeric = 0.0) -> cute.Numeric:
    """reduction_buffer has shape (num_warps / warp_per_row, warps_per_row)
    """
    lane_idx, warp_idx = cute.arch.lane_idx(), cute.arch.warp_idx()
    warps_per_row = cute.size(reduction_buffer.shape[1])
    row_idx, col_idx = warp_idx // warps_per_row, warp_idx % warps_per_row
    if lane_idx == 0:
        reduction_buffer[row_idx, col_idx] = val
    cute.arch.barrier()
    block_reduce_val = init_val
    if lane_idx < warps_per_row:
        block_reduce_val = reduction_buffer[row_idx, lane_idx]
    return warp_reduce(block_reduce_val, op)


@dsl_user_op
def elem_pointer(x: cute.Tensor, coord: cute.Coord, *, loc=None, ip=None) -> cute.Pointer:
    return x.iterator + cute.crd2idx(coord, x.layout, loc=loc, ip=ip)


@dsl_user_op
def set_block_rank(smem_ptr: cute.Pointer, peer_cta_rank_in_cluster: cute.Int32, *, loc=None, ip=None) -> cutlass.Int32:
    """Map the given smem pointer to the address at another CTA rank in the cluster.
    """
    smem_ptr_i32 = smem_ptr.toint(loc=loc, ip=ip).ir_value()
    return cutlass.Int32(
        llvm.inline_asm(
            T.i32(),
            [smem_ptr_i32, peer_cta_rank_in_cluster.ir_value()],
            "mapa.shared::cluster.u32 $0, $1, $2;",
            "=r,r,r",
            has_side_effects=False,
            is_align_stack=False,
            asm_dialect=llvm.AsmDialect.AD_ATT,
        )
    )


@dsl_user_op
def store_shared_remote(
    val: float | cute.Float32, smem_ptr: cute.Pointer, mbar_ptr: cute.Pointer,
    peer_cta_rank_in_cluster: cute.typing.Int, *, loc=None, ip=None
) -> None:
    remote_smem_ptr_i32 = set_block_rank(smem_ptr, peer_cta_rank_in_cluster, loc=loc, ip=ip).ir_value()
    remote_mbar_ptr_i32 = set_block_rank(mbar_ptr, peer_cta_rank_in_cluster, loc=loc, ip=ip).ir_value()
    llvm.inline_asm(
        None,
        [remote_smem_ptr_i32, cute.Float32(val).ir_value(loc=loc, ip=ip), remote_mbar_ptr_i32],
        "st.async.shared::cluster.mbarrier::complete_tx::bytes.f32 [$0], $1, [$2];",
        "r,f,r",
        has_side_effects=True,
        is_align_stack=False,
        asm_dialect=llvm.AsmDialect.AD_ATT,
    )


@cute.jit
def cluster_reduce(val: cute.Numeric, op: Callable, reduction_buffer: cute.Tensor, mbar_ptr: cute.Pointer, init_val: cute.Numeric = 0.0) -> cute.Numeric:
    """reduction_buffer has shape (num_warps / warps_per_row, (warps_per_row, cluster_n))
    """
    cta_rank_in_cluster = cute.arch.block_idx_in_cluster()
    lane_idx, warp_idx = cute.arch.lane_idx(), cute.arch.warp_idx()
    warps_per_row, cluster_n = reduction_buffer.shape[1]
    row_idx, col_idx = warp_idx // warps_per_row, warp_idx % warps_per_row
    if lane_idx < cluster_n:
        store_shared_remote(
            val, elem_pointer(reduction_buffer, (row_idx, (col_idx, cta_rank_in_cluster))),
            mbar_ptr, peer_cta_rank_in_cluster=lane_idx
        )
    cute.arch.mbarrier_wait(mbar_ptr, phase=0)
    block_reduce_val = init_val
    num_iter = cute.ceil_div(warps_per_row * cluster_n, cute.arch.WARP_SIZE)
    for i in cutlass.range_constexpr(num_iter):
        idx = lane_idx + i * cute.arch.WARP_SIZE
        if idx < cute.size(reduction_buffer, mode=[1]):
            block_reduce_val = op(block_reduce_val, reduction_buffer[row_idx, idx])
    return warp_reduce(block_reduce_val, op)


@cute.jit
def block_or_cluster_reduce(val: cute.Numeric, op: Callable, reduction_buffer: cute.Tensor, mbar_ptr: Optional[cute.Pointer], init_val: cute.Numeric = 0.0) -> cute.Numeric:
    """Perform either block or cluster reduction based on whether mbar_ptr is provided.
    """
    if cutlass.const_expr(mbar_ptr is None):
        return block_reduce(val, op, reduction_buffer, init_val=init_val)
    else:
        return cluster_reduce(val, op, reduction_buffer, mbar_ptr, init_val=init_val)


@cute.jit
def row_reduce(
    x: cute.TensorSSA | cute.Numeric,
    op: cute.ReductionOp,
    threads_per_row: cutlass.Constexpr[int],
    reduction_buffer: Optional[cute.Tensor] = None,
    mbar_ptr: Optional[cute.Pointer] = None,
    init_val: cute.Numeric = 0.0,
    hook_fn: Optional[Callable] = None,
) -> cute.Numeric:
    """reduction_buffer must have shape (num_warps / warps_per_row, (warps_per_row, cluster_n))
    """
    if cutlass.const_expr(isinstance(x, cute.TensorSSA)):
        val = x.reduce(op, init_val=init_val, reduction_profile=0)
    else:
        val = x
    warp_op = {
        cute.ReductionOp.ADD: operator.add,
        cute.ReductionOp.MAX: cute.arch.fmax if cutlass.const_expr(x.dtype == cute.Float32) else max,
        cute.ReductionOp.MIN: min,
        cute.ReductionOp.MUL: operator.mul,
    }[op]
    val = warp_reduce(
        val,
        warp_op,
        width=min_constexpr(threads_per_row, cute.arch.WARP_SIZE),
    )
    if cutlass.const_expr(hook_fn is not None):
        hook_fn()
    if cutlass.const_expr(reduction_buffer is not None):
        warps_per_row, cluster_n = reduction_buffer.shape[1]
        assert cluster_n == 1 or mbar_ptr is not None, "mbar_ptr must be provided for cluster reduction"
        if cutlass.const_expr(warps_per_row > 1 or cluster_n > 1):
            val = block_or_cluster_reduce(
                val, warp_op, reduction_buffer, mbar_ptr, init_val=init_val
            )
    return val



def exp2f(x: cute.TensorSSA | cutlass.Float32) -> cute.TensorSSA | cutlass.Float32:
    """exp2f calculation for both vector and scalar.

    :param x: input value
    :type x: cute.TensorSSA or cutlass.Float32
    :return: exp2 value
    :rtype: cute.TensorSSA or cutlass.Float32
    """
    if isinstance(x, cute.TensorSSA):
        res = cute.make_fragment(x.shape, cutlass.Float32)
        res.store(x)
        for i in range(cute.size(x.shape)):
            res[i] = cute.arch.exp2(res[i])
        return res.load()
    else:
        return cute.arch.exp2(x)


@dsl_user_op
def log2f(a: float | cutlass.Float32, *, loc=None, ip=None) -> cutlass.Float32:
    return cutlass.Float32(
        llvm.inline_asm(
            T.f32(),
            [cutlass.Float32(a).ir_value(loc=loc, ip=ip)],
            "lg2.approx.ftz.f32 $0, $1;",
            "=f,f",
            has_side_effects=False,
            is_align_stack=False,
            asm_dialect=llvm.AsmDialect.AD_ATT,
        )
    )


@dsl_user_op
def rsqrt(a: float | cute.Float32, *, loc=None, ip=None) -> cute.Float32:
    return cute.Float32(
        llvm.inline_asm(
            T.f32(),
            [cute.Float32(a).ir_value(loc=loc, ip=ip)],
            "rsqrt.approx.ftz.f32 $0, $1;",
            "=f,f",
            has_side_effects=False,
            is_align_stack=False,
            asm_dialect=llvm.AsmDialect.AD_ATT,
        )
    )


def predicate_k(tAcA: cute.Tensor, limit: cutlass.Int32) -> cute.Tensor:
    # Only compute predicates for the "k" dimension. For the mn dimension, we will use "if"
    tApA = cute.make_fragment(
        cute.make_layout(
            (cute.size(tAcA, mode=[0, 1]), cute.size(tAcA, mode=[1]), cute.size(tAcA, mode=[2])),
            stride=(cute.size(tAcA, mode=[2]), 0, 1),
        ),
        cutlass.Boolean,
    )
    for rest_v in range(tApA.shape[0]):
        for rest_k in range(tApA.shape[2]):
            tApA[rest_v, 0, rest_k] = cute.elem_less(tAcA[(0, rest_v), 0, rest_k][1], limit)
    return tApA
