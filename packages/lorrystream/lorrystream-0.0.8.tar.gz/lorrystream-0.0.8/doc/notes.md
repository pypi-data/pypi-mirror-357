---
orphan: true
---

```python
FAILED tests/test_engine.py::test_mqtt_to_sql - RuntimeError: Message publish failed: The client is not currently connected.

        # Run machinery and publish reading.
        async with engine_single_shot(channel):
>           capmqtt.publish("testdrive/readings", payload)
```

tests/test_engine.py:89:

-- https://github.com/daq-tools/lorrystream/actions/runs/9881854198/job/27293500447?pr=114#step:5:95


```python
     def cratedb(cratedb_service):
>       cratedb_service.reset(
            [
                "testdrive-amqp",
                "testdrive-mqtt",
            ]
        )
E       AttributeError: 'GenCounter' object has no attribute 'reset'
```

ERROR tests/test_engine.py::test_amqp_to_sql - AttributeError: 'GenCounter' object has no attribute 'reset'

-- https://github.com/daq-tools/lorrystream/actions/runs/9881853322/job/27293497538?pr=112#step:5:84
