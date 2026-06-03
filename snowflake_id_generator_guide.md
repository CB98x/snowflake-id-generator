# Build a Snowflake ID Generator in Python

A hands-on project guide. Work through each section in order. Don't skip ahead, and don't worry about speed.

---

## What you're building

A Python class that generates unique 64-bit IDs using the Twitter Snowflake approach, plus a decoder that can take any ID and tell you exactly when, where, and how it was created. By the end you'll understand bitwise operations, epoch math, and why this pattern matters in distributed systems.

## Setup

Create a new folder in your projects directory:

```
mkdir snowflake-id-generator
cd snowflake-id-generator
```

You don't need a virtual environment for this one. No external packages. Just Python and your brain.

Create two files:
- `snowflake.py` (your generator class)
- `test_snowflake.py` (where you'll verify it works)

---

## Part 1: Understand the bit layout

Before writing any code, get this into your head. A Snowflake ID is a single 64-bit integer, but it's actually 5 pieces of information packed together:

```
| 1 bit  | 41 bits    | 5 bits        | 5 bits     | 12 bits         |
| sign   | timestamp  | datacenter_id | machine_id | sequence_number |
| always 0 |          |               |            |                 |
```

Think of it like a license plate that encodes the state, county, and registration year all in one string, except here it's bits instead of letters.

### Your task

Open a Python REPL (just type `python` in your terminal) and try these to build intuition:

```python
# How many milliseconds can 41 bits hold?
print(2**41 - 1)  # this is your max timestamp

# How many datacenters can 5 bits represent?
print(2**5)

# How many machines per datacenter?
print(2**5)

# How many IDs per millisecond per machine?
print(2**12)
```

Write down what each prints. These numbers will come back later.

**Checkpoint:** You should be able to answer: "What's the maximum number of unique IDs a single machine can generate in one millisecond?" If you can, move on.

---

## Part 2: Learn bitwise operations (the scary part that isn't actually scary)

Bitwise operations are just a way to pack and unpack numbers into specific positions within a larger number. You need three operations:

### Left shift (`<<`)

Moves bits to the left by N positions. This is like multiplying by 2^N but for specific bit positions.

```python
# Try in your REPL:
x = 1
print(bin(x))         # 0b1
print(bin(x << 3))    # 0b1000  (the 1 moved 3 positions left)

# What's happening: you're making room for other bits to the right
print(5 << 4)          # 5 * (2**4) = 80
print(bin(5))          # 0b101
print(bin(5 << 4))     # 0b1010000  (the 101 moved 4 positions left)
```

### Bitwise OR (`|`)

Combines bits from two numbers. If either number has a 1 in a position, the result has a 1.

```python
# Try in your REPL:
a = 0b1100  # 12
b = 0b0011  # 3
print(bin(a | b))  # 0b1111 (15) - combined!

# This is how we "place" values into their bit positions
timestamp_bits = 5 << 4    # 0b1010000
machine_bits = 3           # 0b0000011
combined = timestamp_bits | machine_bits  # 0b1010011
print(bin(combined))
```

### Right shift (`>>`) and bitwise AND (`&`)

Used to EXTRACT values back out. Right shift moves bits right. AND masks out the bits you don't want.

```python
# If combined = 0b1010011 and we want to get the machine_bits back:
# Step 1: shift right to move target bits to position 0
print(bin(combined >> 4))  # shifts the timestamp part down

# Step 2: AND with a mask to keep only the bits we want
mask = 0b1111  # keeps lowest 4 bits
print(combined >> 4 & mask)  # should give us back 5
```

### Your task

Play with these in your REPL until the following makes sense to you:

```python
# Pack two numbers into one:
color = 7       # 3 bits (0-7)
size = 12       # 4 bits (0-15)

packed = (size << 3) | color
print(f"Packed: {packed} = {bin(packed)}")

# Unpack them:
extracted_color = packed & 0b111          # mask lowest 3 bits
extracted_size = (packed >> 3) & 0b1111   # shift right 3, mask lowest 4

print(f"Color: {extracted_color}")  # should be 7
print(f"Size: {extracted_size}")    # should be 12
```

**Checkpoint:** If you can pack two numbers together and extract them back out, you understand everything you need. The Snowflake ID just does this with 5 fields instead of 2.

---

## Part 3: Timestamps and epochs

The Snowflake timestamp isn't "time since 1970" (the Unix epoch). It's "time since a custom epoch" so the 41 bits last longer.

```python
import time

# Current time in milliseconds since Unix epoch (Jan 1, 1970)
now_ms = int(time.time() * 1000)
print(f"Milliseconds since 1970: {now_ms}")

# Twitter's custom epoch: Nov 04, 2010
TWITTER_EPOCH = 1288834974657

# Timestamp relative to custom epoch (much smaller number, fits in 41 bits longer)
relative_ts = now_ms - TWITTER_EPOCH
print(f"Milliseconds since Twitter epoch: {relative_ts}")

# Does it fit in 41 bits?
max_41_bits = 2**41 - 1
print(f"Max 41-bit value: {max_41_bits}")
print(f"Our timestamp fits: {relative_ts < max_41_bits}")
```

### Your task

Pick your own custom epoch. Use your birthday, or the current date, or whatever. Just make sure it's in the past and expressed as milliseconds since Jan 1, 1970 UTC.

```python
# Example: if your epoch is June 15, 2005
# You can calculate it like this:
from datetime import datetime, timezone
my_epoch = int(datetime(2005, 6, 15, tzinfo=timezone.utc).timestamp() * 1000)
print(f"My custom epoch: {my_epoch}")
```

Write this down. You'll hardcode it in your class.

**Checkpoint:** You should understand why a custom epoch extends the usable lifespan of the 41-bit timestamp.

---

## Part 4: Build the generator class

Now you're ready. Open `snowflake.py` and build this piece by piece.

### Step 4a: Class skeleton

Start with just the structure and constants. Don't write generate() yet.

```python
import time
import threading


class SnowflakeGenerator:
    # Bit allocation
    SIGN_BITS = 1
    TIMESTAMP_BITS = 41
    DATACENTER_BITS = 5
    MACHINE_BITS = 5
    SEQUENCE_BITS = 12

    # Your custom epoch (replace with yours!)
    EPOCH = ___  # fill this in from Part 3

    # Max values (use bit shifts to calculate these)
    MAX_DATACENTER_ID = ___  # hint: (1 << DATACENTER_BITS) - 1
    MAX_MACHINE_ID = ___
    MAX_SEQUENCE = ___

    def __init__(self, datacenter_id: int, machine_id: int):
        # Validate inputs
        if datacenter_id < 0 or datacenter_id > self.MAX_DATACENTER_ID:
            raise ValueError(f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}")
        if machine_id < 0 or machine_id > self.MAX_MACHINE_ID:
            raise ValueError(f"Machine ID must be between 0 and {self.MAX_MACHINE_ID}")

        self.datacenter_id = datacenter_id
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1

        # We'll need this later for thread safety
        self._lock = threading.Lock()
```

**Your task:** Fill in the three `___` blanks. Run the file and make sure you can create an instance:

```python
# In your REPL or test file:
from snowflake import SnowflakeGenerator
gen = SnowflakeGenerator(datacenter_id=1, machine_id=1)
print(gen.MAX_DATACENTER_ID)   # should print 31
print(gen.MAX_MACHINE_ID)      # should print 31
print(gen.MAX_SEQUENCE)        # should print 4095
```

### Step 4b: The timestamp helper

Add this method to your class:

```python
    def _current_timestamp(self) -> int:
        """Returns milliseconds since our custom epoch."""
        return int(time.time() * 1000) - self.EPOCH
```

Simple, but important. Every ID you generate will call this.

### Step 4c: The generate method (the core)

This is the heart of it. Think through these cases before coding:

1. **Normal case:** timestamp is newer than the last one. Reset sequence to 0, generate ID.
2. **Same millisecond:** timestamp equals the last one. Increment sequence.
3. **Sequence overflow:** if sequence hits max within the same millisecond, wait for the next millisecond.
4. **Clock went backward:** this is bad. Raise an error. (In production you'd handle this more gracefully, but for now just refuse.)

Try writing this yourself first. Here's the structure:

```python
    def generate(self) -> int:
        with self._lock:
            timestamp = self._current_timestamp()

            # Case 4: clock moved backward
            if timestamp < self.last_timestamp:
                raise Exception(
                    f"Clock moved backwards! Refusing to generate ID. "
                    f"Last timestamp: {self.last_timestamp}, current: {timestamp}"
                )

            # Case 2 & 3: same millisecond
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    # Case 3: sequence overflow, wait for next ms
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                # Case 1: new millisecond
                self.sequence = 0

            self.last_timestamp = timestamp

            # NOW: pack everything into a 64-bit integer
            # This is where your bit shifting knowledge pays off
            #
            # Layout reminder:
            # [0][timestamp - 41 bits][datacenter - 5 bits][machine - 5 bits][sequence - 12 bits]
            #
            # YOUR TASK: write the bit packing line below
            # Hint: shift each component left by the total number of bits to its RIGHT
            #
            # timestamp needs to shift left by (5 + 5 + 12) = 22 bits
            # datacenter_id needs to shift left by (5 + 12) = 17 bits
            # machine_id needs to shift left by 12 bits
            # sequence doesn't shift (it's already in the rightmost position)
            #
            # Then OR them all together

            snowflake_id = ___  # YOUR CODE HERE

            return snowflake_id

    def _wait_next_millis(self, last_timestamp: int) -> int:
        """Spin until we get a new millisecond."""
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp
```

**Your task:** Write the single line that creates `snowflake_id` by shifting and OR-ing the four components together. This is the entire point of the project. Take your time.

### Step 4d: Test your generator

Add this to `test_snowflake.py`:

```python
from snowflake import SnowflakeGenerator

gen = SnowflakeGenerator(datacenter_id=1, machine_id=1)

# Generate a few IDs
ids = [gen.generate() for _ in range(10)]

for i, id_val in enumerate(ids):
    print(f"ID {i}: {id_val}")

# Basic checks
print(f"\nAll unique: {len(ids) == len(set(ids))}")
print(f"All positive: {all(i > 0 for i in ids)}")
print(f"Sorted (time-ordered): {ids == sorted(ids)}")
print(f"Fits in 64 bits: {all(i < 2**63 for i in ids)}")
```

Run it. All four checks should print True. If they don't, debug before moving on.

---

## Part 5: Build the decoder

This is the reverse of generate(). Given an ID, extract all four components.

```python
    def decode(self, snowflake_id: int) -> dict:
        """
        Takes a snowflake ID and extracts its components.

        YOUR TASK: use right shift (>>) and AND (&) to extract each field.

        Remember the layout:
        [0][timestamp - 41 bits][datacenter - 5 bits][machine - 5 bits][sequence - 12 bits]

        To extract a field:
        1. Right-shift to move it to position 0
        2. AND with a mask to keep only the bits you want

        The mask for N bits is: (1 << N) - 1
        Example: mask for 5 bits = (1 << 5) - 1 = 31 = 0b11111
        """
        # Extract sequence (rightmost 12 bits, no shift needed)
        sequence = snowflake_id & ___

        # Extract machine_id (next 5 bits)
        machine_id = (snowflake_id >> ___) & ___

        # Extract datacenter_id (next 5 bits)
        datacenter_id = (snowflake_id >> ___) & ___

        # Extract timestamp (next 41 bits)
        timestamp = (snowflake_id >> ___) & ___

        # Convert timestamp back to human-readable UTC
        from datetime import datetime, timezone
        epoch_ms = timestamp + self.EPOCH
        created_at = datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc)

        return {
            "id": snowflake_id,
            "timestamp_ms": timestamp,
            "created_at": created_at.isoformat(),
            "datacenter_id": datacenter_id,
            "machine_id": machine_id,
            "sequence": sequence,
        }
```

**Your task:** Fill in all the `___` blanks. The shift amounts should mirror what you did in generate(), just in reverse.

### Test the decoder

Add to `test_snowflake.py`:

```python
# Generate an ID and decode it
gen = SnowflakeGenerator(datacenter_id=7, machine_id=23)
test_id = gen.generate()
decoded = gen.decode(test_id)

print(f"\nDecoded ID {test_id}:")
for key, value in decoded.items():
    print(f"  {key}: {value}")

# Verify the decoded values match what we put in
assert decoded["datacenter_id"] == 7, f"Expected 7, got {decoded['datacenter_id']}"
assert decoded["machine_id"] == 23, f"Expected 23, got {decoded['machine_id']}"
print("\nDecode verification passed!")
```

---

## Part 6: Stress test it

This is where you prove it actually works under pressure.

```python
import time
from snowflake import SnowflakeGenerator

gen = SnowflakeGenerator(datacenter_id=1, machine_id=1)

# Generate 10,000 IDs as fast as possible
start = time.time()
ids = [gen.generate() for _ in range(10_000)]
elapsed = time.time() - start

print(f"Generated 10,000 IDs in {elapsed:.4f} seconds")
print(f"Rate: {10_000 / elapsed:.0f} IDs/second")
print(f"All unique: {len(ids) == len(set(ids))}")
print(f"All sorted: {ids == sorted(ids)}")

# Simulate two "machines"
gen_a = SnowflakeGenerator(datacenter_id=1, machine_id=1)
gen_b = SnowflakeGenerator(datacenter_id=1, machine_id=2)

ids_a = [gen_a.generate() for _ in range(1000)]
ids_b = [gen_b.generate() for _ in range(1000)]

all_ids = ids_a + ids_b
print(f"\nTwo machines, 2000 total IDs")
print(f"All unique across machines: {len(all_ids) == len(set(all_ids))}")
```

---

## Part 7: Think about what you built

After everything passes, open a new file called `reflections.md` and answer these questions in your own words. These are the kinds of things an interviewer would ask as follow-ups:

1. Why can't we just use auto-increment IDs in a distributed system?
2. What happens to our Snowflake IDs if two machines accidentally get assigned the same datacenter_id AND machine_id?
3. Why does clock going backward cause a problem? What would happen if we just ignored it?
4. Our 41-bit timestamp gives us ~69 years. What would you do when those 69 years run out?
5. If you needed more than 4096 IDs per millisecond on a single machine, how would you change the bit layout? What tradeoff would you be making?
6. Why did we use a threading lock? What could go wrong without it?
7. How is this different from UUID? When would you pick UUID over Snowflake?

---

## You're done!

When you come back, we'll go through your code together, I'll quiz you on the concepts, and we can decide if you want to extend this into a FastAPI service (Phase 2) or move on to something else.

The whole point is that you now have muscle memory for bitwise ops, understand epoch math, and can talk about distributed ID generation from experience, not just from reading a ByteByteGo chapter.

Good luck, take your time, and don't be afraid to sit in the REPL for an hour just playing with `<<` and `|`. That's not wasting time, that's learning.
