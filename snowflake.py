import time
import threading
from datetime import datetime, timezone


class SnowflakeGenerator:
    # Bit allocation
    SIGN_BITS = 1
    TIMESTAMP_BITS = 41
    DATACENTER_BITS = 5
    MACHINE_BITS = 5
    SEQUENCE_BITS = 12

    # Custom epoch: Jan 1, 2025 UTC (change to your own!)
    EPOCH = int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)

    # Max values
    MAX_DATACENTER_ID = (1 << 5) - 1   # 31
    MAX_MACHINE_ID = (1 << 5) - 1      # 31
    MAX_SEQUENCE = (1 << 12) - 1       # 4095

    def __init__(self, datacenter_id: int, machine_id: int):
        if datacenter_id < 0 or datacenter_id > self.MAX_DATACENTER_ID:
            raise ValueError(f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}")
        if machine_id < 0 or machine_id > self.MAX_MACHINE_ID:
            raise ValueError(f"Machine ID must be between 0 and {self.MAX_MACHINE_ID}")

        self.datacenter_id = datacenter_id
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()

    def _current_timestamp(self) -> int:
        """Returns milliseconds since our custom epoch."""
        return int(time.time() * 1000) - self.EPOCH

    def generate(self) -> int:
        with self._lock:
            timestamp = self._current_timestamp()

            # Case: clock moved backward
            if timestamp < self.last_timestamp:
                raise Exception(
                    f"Clock moved backwards! Refusing to generate ID. "
                    f"Last timestamp: {self.last_timestamp}, current: {timestamp}"
                )

            # Case: same millisecond
            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    # Sequence overflow, wait for next ms
                    timestamp = self._wait_next_millis(self.last_timestamp)
            else:
                # New millisecond
                self.sequence = 0

            self.last_timestamp = timestamp

            # Pack everything into a 64-bit integer
            snowflake_id = (
                (timestamp << 22)
                | (self.datacenter_id << 17)
                | (self.machine_id << 12)
                | self.sequence
            )

            return snowflake_id

    def _wait_next_millis(self, last_timestamp: int) -> int:
        """Spin until we get a new millisecond."""
        timestamp = self._current_timestamp()
        while timestamp <= last_timestamp:
            timestamp = self._current_timestamp()
        return timestamp

    def decode(self, snowflake_id: int) -> dict:
        """Takes a snowflake ID and extracts its components."""
        # Extract each field
        sequence = snowflake_id & ((1 << 12) - 1)
        machine_id = (snowflake_id >> 12) & ((1 << 5) - 1)
        datacenter_id = (snowflake_id >> 17) & ((1 << 5) - 1)
        timestamp = (snowflake_id >> 22) & ((1 << 41) - 1)

        # Convert timestamp back to human-readable UTC
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