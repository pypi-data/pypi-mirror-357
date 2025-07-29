"""
Pallas 커널을 사용한 `unique_filled` 연산의 데모 구현.

이 스크립트는 두 가지 구현을 포함합니다:
1. `original_unique_filled`: `jnp.unique`를 사용한 순수 JAX 구현.
2. `pallas_hybrid_unique_filled`: 모든 알려진 한계와 버그를 우회한,
   Byte-Packing과 조건부 로딩을 사용한 최종 Pallas 구현.

두 함수의 결과를 비교하여 Pallas 구현의 정확성을 검증합니다.
"""

import jax
# JAX에서 64비트 정밀도를 사용하도록 맨 처음에 활성화합니다.
jax.config.update("jax_enable_x64", True)
import jax.numpy as jnp
from jax.experimental import pallas as pl

import numpy as np
import time


def original_unique_filled(bytes_data: jnp.ndarray, filled_mask: jnp.ndarray) -> jnp.ndarray:
    """jnp.unique를 사용한 표준 JAX 구현입니다."""
    batch_len = bytes_data.shape[0]
    unique_bytes_idx = jnp.unique(
        bytes_data, axis=0, size=batch_len, return_index=True
    )[1]
    unique_mask = jnp.zeros((batch_len,), dtype=jnp.bool_).at[unique_bytes_idx].set(True)
    return jnp.logical_and(filled_mask, unique_mask)


def pallas_hybrid_unique_filled(bytes_data: jnp.ndarray, filled_mask: jnp.ndarray) -> jnp.ndarray:
    """
    Pallas와 lax.sort를 결합한 하이브리드 구현입니다.
    feature_dim > 8인 경우, 안정성을 위해 원래의 JAX 구현으로 대체됩니다.
    """
    batch_size, feature_dim = bytes_data.shape
    
    # Pallas 커널은 8바이트(64비트)를 초과하는 feature_dim을 직접 지원하지 않습니다.
    # 이 경우, 안정성을 위해 원래의 JAX 구현으로 대체(fallback)합니다.
    if feature_dim > 8:
        return original_unique_filled(bytes_data, filled_mask)

    packed_dtype = jnp.uint64
    # 패딩 값으로 0을 사용하고, 유효한 값은 1부터 시작하도록 하여 충돌을 피합니다.
    padding_value = packed_dtype(0)

    # [Step 1: Pallas Pre-process & Pack Kernel]
    def preprocess_and_pack_kernel(bytes_ref, filled_ref, padding_value_ref, packed_keys_out_ref):
        i = pl.program_id(axis=0)
        
        packed_val = packed_dtype(0)
        for j in range(feature_dim):
            byte = pl.load(bytes_ref, (i, j)).astype(packed_dtype)
            packed_val |= byte << (8 * (feature_dim - 1 - j))
        
        is_filled = pl.load(filled_ref, (i,))
        result = (packed_val + 1) * is_filled.astype(packed_dtype)
        packed_keys_out_ref[i] = result

    packed_keys_shape = jax.ShapeDtypeStruct((batch_size,), packed_dtype)
    
    packed_keys = pl.pallas_call(
        preprocess_and_pack_kernel,
        out_shape=packed_keys_shape,
        grid=(batch_size,),
    )(bytes_data, filled_mask, padding_value)

    # [Step 2: JAX Sort on 1D Arrays]
    original_indices = jnp.arange(batch_size, dtype=jnp.uint32)
    sorted_packed_keys, sorted_indices = jax.lax.sort(
        (packed_keys, original_indices), num_keys=1
    )

    # [Step 3: Pallas Post-process Kernel on Packed Data]
    def find_unique_on_packed_keys_kernel(sorted_keys_ref, sorted_indices_ref, padding_value_ref, unique_filled_out_ref):
        i = pl.program_id(axis=0)
        
        current_key = pl.load(sorted_keys_ref, (i,))
        
        # BUG FIX: 커널 인자로 받은 padding_value_ref는 MemRef 타입이므로,
        # 사용하기 전에 pl.load를 통해 값을 명시적으로 로드해야 합니다.
        padding_val_loaded = pl.load(padding_value_ref, ())
        is_padding = current_key == padding_val_loaded

        is_first = i == 0
        # Ensure we don't read out of bounds
        prev_key = pl.load(sorted_keys_ref, (jnp.maximum(0, i - 1),))
        
        # 패딩이 아니면서, (첫 번째 원소이거나 이전 원소와 다른 경우)에만 unique합니다.
        is_unique = ~is_padding & (is_first | (current_key != prev_key))

        result = is_unique
        original_idx = pl.load(sorted_indices_ref, (i,))
        unique_filled_out_ref[original_idx] = result
    
    unique_filled = pl.pallas_call(
        find_unique_on_packed_keys_kernel,
        out_shape=jax.ShapeDtypeStruct(filled_mask.shape, filled_mask.dtype),
        grid=(batch_size,),
    )(sorted_packed_keys, sorted_indices, padding_value)
    
    return unique_filled


def generate_random_data(key, batch_size, feature_dim, fill_ratio, duplicate_ratio):
    """벤치마킹을 위한 대규모 랜덤 데이터를 생성합니다."""
    keys = jax.random.split(key, 4)
    num_valid = int(batch_size * fill_ratio)
    num_unique_valid = int(num_valid * (1 - duplicate_ratio))

    # 고유한 원본 데이터 생성
    unique_data = jax.random.randint(
        keys[0], (num_unique_valid, feature_dim), 0, 256, dtype=jnp.uint8
    )

    # 중복 데이터 생성 (원본에서 샘플링)
    num_duplicates = num_valid - num_unique_valid
    duplicate_indices = jax.random.randint(keys[1], (num_duplicates,), 0, num_unique_valid)
    duplicate_data = unique_data[duplicate_indices]

    valid_data = jnp.concatenate([unique_data, duplicate_data])
    valid_data = jax.random.permutation(keys[2], valid_data)

    padding = jnp.zeros((batch_size - num_valid, feature_dim), dtype=jnp.uint8)
    bytes_data = jnp.concatenate([valid_data, padding])

    filled_mask = jnp.concatenate(
        [
            jnp.ones(num_valid, dtype=jnp.bool_),
            jnp.zeros(batch_size - num_valid, dtype=jnp.bool_),
        ]
    )
    return bytes_data, filled_mask


def run_benchmark(func, *args, num_runs=10):
    """함수의 실행 시간을 측정하고 JIT 워밍업을 처리합니다."""
    # JIT 컴파일을 위한 워밍업 실행
    func(*args).block_until_ready()
    
    start_time = time.time()
    for _ in range(num_runs):
        func(*args).block_until_ready()
    end_time = time.time()
    
    avg_time_ms = ((end_time - start_time) / num_runs) * 1000
    return avg_time_ms


if __name__ == "__main__":
    # --- 벤치마크 설정 ---
    BATCH_SIZE = 100_000
    FEATURE_DIM = 8  # Pallas 커널은 8 이하만 지원
    FILL_RATIO = 0.8
    DUPLICATE_RATIO = 0.3 # 유효한 데이터 중 중복 비율
    NUM_RUNS = 20
    # ---------------------

    key = jax.random.PRNGKey(0)
    bytes_data, filled_mask = generate_random_data(
        key, BATCH_SIZE, FEATURE_DIM, FILL_RATIO, DUPLICATE_RATIO
    )
    
    print("--- Benchmark Setup ---")
    print(f"Batch Size: {BATCH_SIZE:,}")
    print(f"Feature Dim: {FEATURE_DIM}")
    print(f"Fill Ratio: {FILL_RATIO:.1f}")
    print(f"Duplicate Ratio: {DUPLICATE_RATIO:.1f}")
    print(f"Number of Runs: {NUM_RUNS}\n")

    # JIT 컴파일
    jitted_original = jax.jit(original_unique_filled)
    jitted_pallas = jax.jit(pallas_hybrid_unique_filled)

    # 벤치마킹 실행
    print("--- Running Benchmarks ---")
    print("Warming up JIT compilers...")
    
    original_time = run_benchmark(jitted_original, bytes_data, filled_mask, num_runs=NUM_RUNS)
    pallas_time = run_benchmark(jitted_pallas, bytes_data, filled_mask, num_runs=NUM_RUNS)

    print("\n--- Benchmark Results ---")
    print(f"Avg. time for Original JAX: {original_time:.4f} ms")
    print(f"Avg. time for Pallas Hybrid: {pallas_time:.4f} ms")

    # 성능 비교
    if pallas_time < original_time:
        speedup = (original_time / pallas_time)
        print(f"\n✅ Pallas is {speedup:.2f}x faster.")
    else:
        slowdown = (pallas_time / original_time)
        print(f"\n❌ Pallas is {slowdown:.2f}x slower.")
        
    # 정확성 검증 (첫 실행으로)
    print("\n--- Correctness Check ---")
    original_result = jitted_original(bytes_data, filled_mask)
    pallas_result = jitted_pallas(bytes_data, filled_mask)
    try:
        np.testing.assert_array_equal(original_result, pallas_result)
        print("✅ Success: Pallas implementation matches the original JAX implementation on random data.")
    except AssertionError as e:
        print(f"❌ Failure: Results do not match on random data.\n{e}")
