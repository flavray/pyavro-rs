from pyavro_rs import Reader
from pyavro_rs import Schema
from pyavro_rs import Writer


def test_serde():
    schema_json = """
    {
        "type": "record",
        "name": "test",
        "fields": [
            {"name": "a", "type": "long", "default": 42},
            {"name": "b", "type": "string"}
        ]
    }
    """
    schema = Schema(schema_json)
    writer = Writer(schema)
    writer.append({'a': 27, 'b': 'foo'})
    writer.append({'b': 'bar'})
    writer.flush()
    output = writer.into()
    reader = Reader(output, schema)
    records = [record for record in reader]
    assert records == [{'a': 27, 'b': 'foo'}, {'a': 42, 'b': 'bar'}]
