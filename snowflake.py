import time
import threading

class SnowflakeGenerator:
    #Bit allocation
    SIGN_BITS = 1
    TIMESTAMP_BIT = 41
    DATACENTER_BIT = 5
    MACHINE_BITS = 5
    SEQUENCE_BITS = 12

    EPOCH = 1129593600000

    MAX_DATACENTER_ID = (1 << DATACENTER_BIT) - 1
    MAX_MACHINE_ID = (1 << MACHINE_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

    def __init__(self, datacenter_id: int, machine_id: int):
        #Validating inputs
        if datacenter_id < 0 or datacenter_id > self.MAX_DATACENTER_ID:
            raise ValueError(f"Datacenter ID must be between 0 and {self.MAX_DATACENTER_ID}")
        if machine_id < 0 or machine_id > self.MAX_MACHINE_ID:
            raise ValueError(f"Machine ID shoudl be between 0 and {self.MAX_MACHINE_ID}")
        
        self.datacenter_id = datacenter_id
        self.machine_id = machine_id
        self.sequence = 0
        self.last_timestamp = -1

        self._lock = threading.Lock()

        def _current_timestamp(self) -> int:
            return int(time.time() * 1000) - self.EPOCH
        

        def generate(self) -> int:
            with self._lock:
                timestamp = self._current_tiemstamp()

                #Case: clock moved backward
                if timestamp < self.last_timestamp:
                    raise Exception(f"Clock moced backwards! Refusign to generate ID."
                                    f"Last timestamp: {self.last_timestamp}, current:{timestamp}")
                
                #Case: same millisecond
                if timestamp == self.last_timestamp:
                    self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                    if self.sequence == 0:
                        #case: sequence overflow -> wait for next ms
                        timestamp = self._wait_next_millis(self.last_timestamp)
                else:
                    self.sequence = 0

                self.last_timestamp = timestamp

                