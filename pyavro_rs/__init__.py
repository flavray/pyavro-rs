from cPickle import dumps
from cPickle import loads
from types import NoneType

from pyavro_rs._lowlevel import ffi, lib


CODEC_NULL = lib.AVRO_CODEC_NULL
CODEC_DEFLATE = lib.AVRO_CODEC_DEFLATE
lib.avro_init()


class AvroError(Exception):
    def __init__(self, err, message):
        self.err = err
        self.message = message

    def __repr__(self):
        return 'AvroError(err={}, message={})'.format(self.err, self.message)

    def __str__(self):
        return self.__repr__()


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
    return rustcall(lib.avro_str_from_c_str, ffi.from_buffer(s))  # .encode('utf-8')))


def from_bytearray(ba):
    return bytes(ffi.buffer(ba.data, ba.len)) if ba.data != ffi.NULL else b''


class RustObject(object):
    __dealloc_func__ = None
    __objptr = None

    @classmethod
    def _from_objptr(cls, ptr):
        result = object.__new__(cls)
        result.__objptr = ptr
        return result

    @property
    def _objptr(self):
        if not self.__objptr:
            raise RuntimeError('Object is closed')
        return self.__objptr

    def _methodcall(self, func, *args):
        return rustcall(func, self._objptr, *args)

    def __del__(self):
        if self.__objptr is None:
            return

        f = self.__class__.__dealloc_func__
        if f is not None:
            rustcall(f, self.__objptr)
            self.__objptr = None


class Schema(RustObject):
    __dealloc_func__ = lib.avro_schema_free

    def __new__(cls, schema_str):
        return cls._from_objptr(
            rustcall(
                lib.avro_schema_from_json,
                ffi.addressof(encode_str(schema_str)),
            )
        )


def avro_null(_):
    return rustcall(lib.avro_value_null_new)


def avro_bool(b):
    return rustcall(lib.avro_value_boolean_new, int(b))


def avro_int(n):
    return rustcall(lib.avro_value_long_new, n)


def avro_float(x):
    return rustcall(lib.avro_value_double_new, x)


def avro_str(s):
    return rustcall(lib.avro_value_string_new, encode_str(s))


def avro_bytes(ba):
    if type(ba) == str:  # thank you python2. type('toto') == str == bytes
        return avro_str(ba)
    byte_array = rustcall(lib.avro_byte_array_from_c_array, ba, len(ba))
    return rustcall(lib.avro_value_bytes_new, byte_array)


def avro_list(items):
    array = lib.avro_value_array_new(len(items))
    for item in items:
        value = Value(item)
        lib.avro_array_append(array, value.value)
    return array


def avro_dict(items):
    m = lib.avro_value_map_new(len(items))
    for key, item in items.items():
        if type(key) != str:
            raise Exception('Map keys must be string, got {}'.format(type(key)))
        key_value = encode_str(key)
        item_value = Value(item)
        lib.avro_map_put(m, key_value, item_value.value)
    return m


class Value(RustObject):
    # __dealloc_func__ = lib.avro_value_free  # Values are deallocated on the Rust side

    __TYPE_TO_AVRO = {
        NoneType: avro_null,
        bool: avro_bool,
        int: avro_int,
        long: avro_int,
        float: avro_float,
        str: avro_str,
        bytes: avro_bytes,
        list: avro_list,
        tuple: avro_list,
        dict: avro_dict,
    }

    def __new__(cls, datum):
        fn = cls.__TYPE_TO_AVRO.get(type(datum))
        if fn is None:
            raise Exception('Unable to encode type {}'.format(type(datum)))
        return cls._from_objptr(fn(datum))

    @property
    def value(self):
        return self._objptr


class Writer(RustObject):
    # __dealloc_func__ = lib.avro_writer_free  # TODO: this function does not exist

    def __new__(cls, schema, codec=CODEC_NULL):
        return cls._from_objptr(
            rustcall(
                lib.avro_writer_new,
                schema._objptr,
                codec,
            )
        )

    def _append_old(self, datum):
        pickled = dumps(datum)
        buf = rustcall(lib.avro_byte_array_from_c_array, pickled, len(pickled))
        return self._methodcall(lib.avro_writer_append, ffi.addressof(buf))

    def append(self, datum):
        value = Value(datum)
        self._methodcall(lib.avro_writer_append2, value.value)
        return value

    def flush(self):
        return self._methodcall(lib.avro_writer_flush)

    def into(self):
        byte_array = self._methodcall(lib.avro_writer_into_data)
        return from_bytearray(byte_array)


class Reader(RustObject):
    __dealloc_func__ = lib.avro_reader_free

    def __new__(cls, buf, schema):
        byte_array = rustcall(lib.avro_byte_array_from_c_array, buf, len(buf))
        return cls._from_objptr(
            rustcall(
                lib.avro_reader_new,
                ffi.addressof(byte_array),
                schema._objptr,
            )
        )

    def __iter__(self):
        return self

    def __next__(self):
        item = self._methodcall(lib.avro_reader_read_next)
        if item.len == 0:
            raise StopIteration
        return loads(from_bytearray(item))

    def next(self):
        return self.__next__()
