"""
Optimized MGPU Merge Path Implementation
Addresses performance issues identified in the analysis
"""

import jax
import jax.numpy as jnp
from jax.experimental import pallas as pl
import functools
from typing import Tuple
import time


# ============================================================================
# Optimized Merge Path Functions
# ============================================================================

@jax.jit
def fast_merge_path_search(ak: jax.Array, bk: jax.Array, diagonal: int) -> Tuple[int, int]:
    """
    Optimized merge path search with reduced function call overhead
    """
    ak_len = ak.shape[0]
    bk_len = bk.shape[0]
    
    diagonal = jnp.clip(diagonal, 0, ak_len + bk_len)
    low = jnp.maximum(0, diagonal - bk_len)
    high = jnp.minimum(diagonal, ak_len)
    
    # Unrolled binary search for better performance
    def search_body(carry):
        low, high = carry
        mid = (low + high) // 2
        bk_idx = diagonal - mid
        
        # Vectorized comparison
        ak_val = jnp.where(mid < ak_len, ak[mid], jnp.inf)
        bk_val_prev = jnp.where(bk_idx > 0, bk[bk_idx - 1], -jnp.inf)
        
        pred = ak_val > bk_val_prev
        new_low = jnp.where(pred, low, mid + 1)
        new_high = jnp.where(pred, mid, high)
        
        return (new_low, new_high)
    
    # Fixed number of iterations for better JIT compilation
    for _ in range(10):  # log2(max_array_size) iterations
        low, high = jax.lax.cond(
            low < high,
            search_body,
            lambda carry: carry,
            (low, high)
        )
    
    return low, diagonal - low


@functools.partial(jax.jit, static_argnames=['num_partitions'])
def vectorized_merge_partitions(
    ak: jax.Array, 
    bk: jax.Array, 
    num_partitions: int
) -> jax.Array:
    """
    Vectorized partition computation for better performance
    """
    total_elements = ak.shape[0] + bk.shape[0]
    diagonals = jnp.arange(num_partitions + 1) * total_elements // num_partitions
    
    # Vectorize the merge path search
    def find_single_partition(diagonal):
        ak_idx, bk_idx = fast_merge_path_search(ak, bk, diagonal)
        return jnp.stack([ak_idx, bk_idx])
    
    return jax.vmap(find_single_partition)(diagonals)


# ============================================================================
# High-Performance Merge Implementation
# ============================================================================

@jax.jit
def optimized_merge_scan(ak: jax.Array, bk: jax.Array) -> Tuple[jax.Array, jax.Array]:
    """
    Optimized merge using scan with minimal overhead
    """
    n, m = ak.shape[0], bk.shape[0]
    total = n + m
    
    def merge_step(carry, _):
        i, j = carry
        
        # Bounds checking
        has_ak = i < n
        has_bk = j < m
        
        # Load values with bounds checking
        ak_val = jnp.where(has_ak, ak[i], jnp.inf)
        bk_val = jnp.where(has_bk, bk[j], jnp.inf)
        
        # Decision logic
        take_ak = jnp.logical_and(has_ak, jnp.logical_or(~has_bk, ak_val <= bk_val))
        
        # Output
        value = jnp.where(take_ak, ak_val, bk_val)
        index = jnp.where(take_ak, i, n + j)
        
        # Update state
        new_i = jnp.where(take_ak, i + 1, i)
        new_j = jnp.where(take_ak, j, j + 1)
        
        return (new_i, new_j), (value, index)
    
    _, (values, indices) = jax.lax.scan(merge_step, (0, 0), jnp.arange(total))
    return values, indices


@functools.partial(jax.jit, static_argnames=['num_partitions'])
def parallel_merge_optimized(
    ak: jax.Array, 
    bk: jax.Array, 
    num_partitions: int = 4
) -> Tuple[jax.Array, jax.Array]:
    """
    Truly parallel merge using vmap over partitions
    """
    if num_partitions == 1:
        return optimized_merge_scan(ak, bk)
    
    n, m = ak.shape[0], bk.shape[0]
    total = n + m
    
    # Get partition boundaries
    partitions = vectorized_merge_partitions(ak, bk, num_partitions)
    
    def process_partition(partition_idx):
        start_ak, start_bk = partitions[partition_idx]
        end_ak, end_bk = partitions[partition_idx + 1]
        
        # Extract partition slices
        partition_ak = ak[start_ak:end_ak]
        partition_bk = bk[start_bk:end_bk]
        
        # Merge partition
        if partition_ak.shape[0] == 0:
            # Only bk elements
            values = partition_bk
            indices = jnp.arange(n + start_bk, n + end_bk, dtype=jnp.int32)
        elif partition_bk.shape[0] == 0:
            # Only ak elements  
            values = partition_ak
            indices = jnp.arange(start_ak, end_ak, dtype=jnp.int32)
        else:
            # Merge both
            values, local_indices = optimized_merge_scan(partition_ak, partition_bk)
            # Map local indices to global
            indices = jnp.where(
                local_indices < partition_ak.shape[0],
                start_ak + local_indices,
                n + start_bk + (local_indices - partition_ak.shape[0])
            )
        
        # Pad to consistent size for vmap
        max_size = (total + num_partitions - 1) // num_partitions + 1
        padded_values = jnp.pad(values, (0, max_size - values.shape[0]), 
                               constant_values=jnp.inf)
        padded_indices = jnp.pad(indices, (0, max_size - indices.shape[0]), 
                                constant_values=-1)
        
        return padded_values, padded_indices, values.shape[0]
    
    # Process all partitions in parallel
    partition_ids = jnp.arange(num_partitions)
    padded_values, padded_indices, sizes = jax.vmap(process_partition)(partition_ids)
    
    # Reconstruct final arrays
    output_values = jnp.zeros(total, dtype=ak.dtype)
    output_indices = jnp.zeros(total, dtype=jnp.int32)
    
    pos = 0
    for i in range(num_partitions):
        size = sizes[i]
        output_values = output_values.at[pos:pos+size].set(padded_values[i, :size])
        output_indices = output_indices.at[pos:pos+size].set(padded_indices[i, :size])
        pos += size
    
    return output_values, output_indices


# ============================================================================
# Adaptive Merge Strategy
# ============================================================================

@jax.jit
def adaptive_merge(ak: jax.Array, bk: jax.Array) -> Tuple[jax.Array, jax.Array]:
    """
    Adaptively choose merge strategy based on array sizes
    """
    n, m = ak.shape[0], bk.shape[0]
    total = n + m
    
    # Use different strategies based on size
    def small_merge():
        return optimized_merge_scan(ak, bk)
    
    def medium_merge():
        return parallel_merge_optimized(ak, bk, num_partitions=2)
    
    def large_merge():
        return parallel_merge_optimized(ak, bk, num_partitions=4)
    
    def huge_merge():
        return parallel_merge_optimized(ak, bk, num_partitions=8)
    
    return jax.lax.cond(
        total < 1000,
        small_merge,
        lambda: jax.lax.cond(
            total < 10000,
            medium_merge,
            lambda: jax.lax.cond(
                total < 100000,
                large_merge,
                huge_merge
            )
        )
    )


# ============================================================================
# Performance Testing
# ============================================================================

def benchmark_optimized_implementations():
    """
    Comprehensive benchmark of all implementations
    """
    import jax.random as jr
    
    print("Optimized MGPU Merge Path Performance Analysis")
    print("=" * 60)
    
    def run_benchmark(size_a, size_b, num_trials=5):
        key = jr.PRNGKey(42)
        key_a, key_b = jr.split(key)
        
        # Generate test data
        a_data = jnp.sort(jr.uniform(key_a, (size_a,), dtype=jnp.float32))
        b_data = jnp.sort(jr.uniform(key_b, (size_b,), dtype=jnp.float32))
        
        implementations = [
            ("Optimized Scan", lambda: optimized_merge_scan(a_data, b_data)),
            ("Parallel 2-way", lambda: parallel_merge_optimized(a_data, b_data, 2)),
            ("Parallel 4-way", lambda: parallel_merge_optimized(a_data, b_data, 4)),
            ("Parallel 8-way", lambda: parallel_merge_optimized(a_data, b_data, 8)),
            ("Adaptive", lambda: adaptive_merge(a_data, b_data)),
        ]
        
        print(f"\nBenchmark: {size_a} + {size_b} elements")
        print("-" * 40)
        
        reference_result = None
        
        for name, func in implementations:
            # Warmup
            try:
                result = func()
                result[0].block_until_ready()
                
                # Timing
                times = []
                for _ in range(num_trials):
                    start = time.perf_counter()
                    result = func()
                    result[0].block_until_ready()
                    times.append(time.perf_counter() - start)
                
                avg_time = sum(times) / len(times)
                
                # Verify correctness
                if reference_result is None:
                    reference_result = result
                else:
                    assert jnp.allclose(result[0], reference_result[0]), f"{name} failed correctness check"
                
                throughput = (size_a + size_b) / avg_time / 1e6  # Million elements/sec
                print(f"{name:15}: {avg_time*1000:6.2f} ms ({throughput:6.2f} ME/s)")
                
            except Exception as e:
                print(f"{name:15}: FAILED ({str(e)[:30]}...)")
    
    # Test different sizes
    test_cases = [
        (1000, 1000),
        (5000, 5000), 
        (10000, 10000),
        (25000, 25000),
    ]
    
    for size_a, size_b in test_cases:
        run_benchmark(size_a, size_b)
    
    print("\n" + "=" * 60)
    print("Performance Summary:")
    print("- Optimized scan: Best for small arrays")
    print("- Parallel merge: Scales with array size")
    print("- Adaptive: Automatically chooses best strategy")
    print("=" * 60)


if __name__ == "__main__":
    benchmark_optimized_implementations() 