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


class Writer(RustObject):
    def __new__(cls, schema, codec=CODEC_NULL):
        return cls._from_objptr(
            rustcall(
                lib.avro_writer_new,
                schema._objptr,
                codec,
            )
        )

    def append(self, datum):
        pickled = dumps(datum)
        buf = rustcall(lib.avro_byte_array_from_c_array, pickled, len(pickled))
        return self._methodcall(lib.avro_writer_append, ffi.addressof(buf))

    def flush(self):
        return self._methodcall(lib.avro_writer_flush)

    def into(self):
        return self._methodcall(lib.avro_writer_into_data)


class Reader(RustObject):
    __dealloc_func__ = lib.avro_reader_free

    def __new__(cls, buf, schema):
        # b = rustcall(lib.avro_byte_array_from_c_array, buf, len(buf))
        return cls._from_objptr(
            rustcall(
                lib.avro_reader_new,
                ffi.addressof(buf),
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
