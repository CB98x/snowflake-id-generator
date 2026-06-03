import time
from snowflake import SnowflakeGenerator

# --- Test 1: Basic generation ---
print("=== Basic Generation ===")
gen = SnowflakeGenerator(datacenter_id=1, machine_id=1)

ids = [gen.generate() for _ in range(10)]

for i, id_val in enumerate(ids):
    print(f"ID {i}: {id_val}")

print(f"\nAll unique: {len(ids) == len(set(ids))}")
print(f"All positive: {all(i > 0 for i in ids)}")
print(f"Sorted (time-ordered): {ids == sorted(ids)}")
print(f"Fits in 64 bits: {all(i < 2**63 for i in ids)}")

# --- Test 2: Decode round-trip ---
print("\n=== Decode Round-Trip ===")
gen = SnowflakeGenerator(datacenter_id=7, machine_id=23)
test_id = gen.generate()
decoded = gen.decode(test_id)

print(f"Decoded ID {test_id}:")
for key, value in decoded.items():
    print(f"  {key}: {value}")

assert decoded["datacenter_id"] == 7, f"Expected 7, got {decoded['datacenter_id']}"
assert decoded["machine_id"] == 23, f"Expected 23, got {decoded['machine_id']}"
print("\nDecode verification passed!")

# --- Test 3: Stress test ---
print("\n=== Stress Test ===")
gen = SnowflakeGenerator(datacenter_id=1, machine_id=1)

start = time.time()
ids = [gen.generate() for _ in range(10_000)]
elapsed = time.time() - start

print(f"Generated 10,000 IDs in {elapsed:.4f} seconds")
print(f"Rate: {10_000 / elapsed:.0f} IDs/second")
print(f"All unique: {len(ids) == len(set(ids))}")
print(f"All sorted: {ids == sorted(ids)}")

# --- Test 4: Two machines ---
print("\n=== Two Machines ===")
gen_a = SnowflakeGenerator(datacenter_id=1, machine_id=1)
gen_b = SnowflakeGenerator(datacenter_id=1, machine_id=2)

ids_a = [gen_a.generate() for _ in range(1000)]
ids_b = [gen_b.generate() for _ in range(1000)]

all_ids = ids_a + ids_b
print(f"Two machines, 2000 total IDs")
print(f"All unique across machines: {len(all_ids) == len(set(all_ids))}")