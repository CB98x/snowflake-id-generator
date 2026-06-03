# Snowflake ID Generator

A Python implementation of Twitter's Snowflake ID generation algorithm. Generates unique, time-sortable 64-bit integer IDs without any coordination between machines.

## What is a Snowflake ID?

A single 64-bit integer that packs five pieces of information using bitwise operations:

```
| 1 bit  | 41 bits    | 5 bits        | 5 bits     | 12 bits         |
| sign   | timestamp  | datacenter_id | machine_id | sequence_number |
```

This means each ID encodes when it was created, where it was created, and how many came before it that millisecond. No database lookups, no coordination between machines.

## Why not auto-increment or UUID?

- **Auto-increment** requires a single source of truth. Doesn't scale across distributed systems.
- **UUIDs** are 128 bits, not sortable by time, and random ones have poor database index performance.
- **Snowflake IDs** are 64 bits, naturally time-ordered, and guarantee uniqueness across machines without coordination.

## Usage

```python
from snowflake import SnowflakeGenerator

# Create a generator for a specific machine
gen = SnowflakeGenerator(datacenter_id=1, machine_id=1)

# Generate IDs
id1 = gen.generate()
id2 = gen.generate()

# Decode any ID back into its components
decoded = gen.decode(id1)
print(decoded)
# {
#   'id': 187735204465610752,
#   'timestamp_ms': 44759560696,
#   'created_at': '2026-06-03T01:12:40.696000+00:00',
#   'datacenter_id': 1,
#   'machine_id': 1,
#   'sequence': 0
# }
```

## Capacity

| Component | Bits | Range | Meaning |
|-----------|------|-------|---------|
| Timestamp | 41 | ~69 years | Milliseconds since custom epoch |
| Datacenter | 5 | 0-31 | 32 datacenters |
| Machine | 5 | 0-31 | 32 machines per datacenter |
| Sequence | 12 | 0-4095 | 4,096 IDs per millisecond per machine |

## Running tests

```bash
python test_snowflake.py
```

Runs four test suites: basic generation, decode round-trip, stress test (10k IDs), and cross-machine uniqueness.

## Concepts covered

- Bitwise operations (left shift, right shift, OR, AND)
- Bit packing and unpacking
- Epoch math and custom timestamps
- Thread safety with locks
- Distributed system ID generation

## Built as

A hands-on learning project to build intuition for bitwise operations, epoch math, and distributed ID generation patterns. Based on the Snowflake ID chapter from system design study.

## Requirements

Python 3.7+. No external dependencies.