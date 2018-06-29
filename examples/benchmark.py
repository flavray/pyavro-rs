import json
import time

from pyavro_rs import Reader
from pyavro_rs import Schema
from pyavro_rs import Writer


def write_pyavro_rs(schema, records, runs=1):
    times = []
    for _ in range(runs):
        start = time.time()

        writer = Writer(schema)
        for record in records:
            writer.append(record)
        writer.flush()
        end = time.time()
        output = writer.into()
        times.append(end - start)
    return output, sum(times)


def read_pyavro_rs(schema, bytes_, runs=1):
    times = []
    for _ in range(runs):
        start = time.time()
        records = list(Reader(bytes_, schema))
        end = time.time()
        times.append(end - start)
    return records, sum(times)


small_schema = Schema(json.dumps({
    "type": "record",
    "name": "Test",
    "namespace": "test",
    "fields": [{
        "name": "field",
        "type": {"type": "string"}
    }]
}))

big_schema = Schema(json.dumps({
    "type": "record",
    "name": "userInfo",
    "namespace": "my.example",
    "fields": [{
        "name": "username",
        "type": "string",
        "default": "NONE"
    }, {
        "name": "age",
        "type": "int",
        "default": -1
    }, {
        "name": "phone",
        "type": "string",
        "default": "NONE"
    }, {
        "name": "housenum",
        "type": "string",
        "default": "NONE"
    }, {
        "name": "address",
        "type": {
            "type": "record",
            "name": "mailing_address",
            "fields": [{
                "name": "street",
                "type": "string",
                "default": "NONE"
            }, {
                "name": "city",
                "type": "string",
                "default": "NONE"
            }, {
                "name": "state_prov",
                "type": "string",
                "default": "NONE"
            }, {
                "name": "country",
                "type": "string",
                "default": "NONE"
            }, {
                "name": "zip",
                "type": "string",
                "default": "NONE"
            }]
        },
        "default": {}
    }]
}))

small_record = {'field': 'foo'}
big_record = {
    'username': 'username',
    'age': 10,
    'phone': '000000000',
    'housenum': '0000',
    'address': {
        'street': 'street',
        'city': 'city',
        'state_prov': 'state_prov',
        'country': 'country',
        'zip': 'zip',
    },
}

# Configuration is a tuple of (schema, single_record, num_records, num_runs)
configurations = [
    (small_schema, small_record, 10000, 1),
    (big_schema, big_record, 10000, 1),

    (small_schema, small_record, 1, 100000),
    (small_schema, small_record, 100, 1000),
    (small_schema, small_record, 10000, 10),
    (big_schema, big_record, 1, 100000),
    (big_schema, big_record, 100, 1000),
    (big_schema, big_record, 10000, 10),
]

for schema, single_record, num_records, num_runs in configurations:
    original_records = [single_record for _ in range(num_records)]
    bytes_, time_w = write_pyavro_rs(schema, original_records, runs=num_runs)
    records, time_r = read_pyavro_rs(schema, bytes_, runs=num_runs)

    assert records == original_records

    print('{},{},{},{}'.format(num_records, num_runs, time_w, time_r))
