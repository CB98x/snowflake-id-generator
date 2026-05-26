from snowflake import SnowflakeGenerator

gen = SnowflakeGenerator(datacenter_id=1, machine_id=1)

print(gen.MAX_DATACENTER_ID)
print(gen.MAX_MACHINE_ID)
print(gen.MAX_SEQUENCE)


