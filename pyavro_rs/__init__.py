from pyavro_rs._lowlevel import ffi, lib


# TODO: avro_init


class AvroError(Exception):
    def __init__(self, err, message):
        self.err = err
        self.message = message

    def __repr__(self):
        return 'AvroError(err={}, message={})'.format(self.err, self.message)


def rustcall(func, *args):
    '''Calls rust method and does some error handling.'''
    lib.avro_err_clear()

    result = func(*args)
    err = lib.avro_err_get_last_code()
    if err:
        raise AvroError(err, decode_str(lib.avro_err_get_last_message()))

    return result


def decode_str(s, free=False):
    '''Decodes an AvroStr'''
    try:
        if s.len == 0:
            return u''
        return ffi.unpack(s.data, s.len).decode('utf-8', 'replace')
    finally:
        if free:
            lib.avro_str_free(ffi.addressof(s))


def encode_str(s):
    '''Encodes a AvroStr'''
    return rustcall(lib.avro_str_from_c_str, ffi.from_buffer(s.encode('utf-8')))


def parse_schema(schema_str):
    return rustcall(
        lib.avro_schema_from_json,
        ffi.addressof(encode_str(schema_str))
    )


def free_schema(schema):
    return rustcall(
        lib.avro_schema_free,
        schema,
    )


def new_writer(schema):
    buf = rustcall(lib.avro_byte_array_from_c_array, [], 0)
    return rustcall(
        lib.avro_writer_new,
        schema,
        ffi.addressof(buf),
        lib.AVRO_CODEC_NULL,
    )
