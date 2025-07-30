# kafkaesque-pylib

## Example

```python
from kafkaesque_pylib import KafkaEsqueConfig, KafkaEsqueContext
from datetime import timedelta

TOPIC = 'test-topic'

# 'DEV' is the name of the kafkaesque cluster config
config = KafkaEsqueConfig.get('DEV')
context = KafkaEsqueContext(config)

# take topic config from kafkaesque, currently only string and avro is supported
topic = context.get_topic(TOPIC)
# topic = context.get_topic(TOPIC, key_type='string', value_type='avro')

tracer = topic.trace_all()
# tracer = topic.trace_newest(amount_per_partition=10, partitions=[0])
# tracer = topic.trace_oldest(amount_per_partition=10)
# tracer = topic.trace_by_time(from_time='P7D', until_time=timedelta(days=1), partitions=[1, 2])
# tracer = topic.trace_by_time(from_time='2025-03-20T12:00:00+01:00', amount_per_partition=100)
# tracer = topic.trace_continuously(partitions=[0])
# tracer = topic.trace_from_specific_offset(offset=10, amount_per_partition=100, partitions=[0])

for message in tracer:
    if message.is_erroneous():
        # for example deserialization error
        print(f"error for {message.key}")
        continue
    if message.is_tombstone():
        print(f"tombstone for {message.key}")
        continue
    print(message.key)
    print(message.value)
    print(message.partition)
    print(message.offset)
    print(message.timestamp)
    print(message.header)
    print()

```