from pyavro_rs import decode_str
from pyavro_rs import encode_str
from pyavro_rs import schemaless_read
from pyavro_rs import schemaless_write
from pyavro_rs import Reader
from pyavro_rs import Schema
from pyavro_rs import Writer

s = encode_str('Hello, World!')
print(decode_str(s))

schema = Schema('''{"namespace": "test", "type": "record", "name": "Test", "fields": [{"type": {"type": "string"}, "name": "field"}]}''')
print(schema)

writer = Writer(schema)
print(writer)

writer.append({'field': 'foo'})
writer.append({'field': 'bar'})
writer.flush()

output = writer.into()

reader = Reader(output, schema)

for record in reader:
    print(record)


output = schemaless_write(schema, {'field': 'baz'})
print(schemaless_read(schema, output))
