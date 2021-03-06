#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import struct
import io
import sys


FIELDPARSERS = {
    'b': lambda x: struct.unpack('?', x)[0],
    'o': lambda x: tuple(parse(io.BytesIO(x))),
    'p': lambda x: (x[1:] + b'\00').decode('utf-16'),
    's': lambda x: struct.unpack('>H', x)[0],
    't': lambda x: (x[1:] + b'\00').decode('utf-16'),
    'u': lambda x: struct.unpack('>I', x)[0],
}


def parse(fp):
    for i, header in enumerate(iter(lambda: fp.read(8), b'')):
        assert len(header) == 8
        type_id_ascii, name_ascii, length = struct.unpack('>c3sI', header)

        type_id = type_id_ascii.decode('ascii')
        name = name_ascii.decode('ascii')

        # vrsn field has no type_id, but contains text
        if type_id == 'v' and name == 'rsn':
            name = 'vrsn'
            type_id = 't'

        data = fp.read(length)
        assert len(data) == length

        try:
            fieldparser = FIELDPARSERS[type_id]
        except KeyError:
            value = data
        else:
            value = fieldparser(data)

        yield name, type_id, length, value


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE', type=argparse.FileType('rb'))
    args = parser.parse_args(argv)

    for name, type_id, length, value in parse(args.file):
        if isinstance(value, tuple):
            print('{name}[{type_id}] ({length} B)'.format(
                name=name,
                type_id=type_id,
                length=length,
            ))
            for name, type_id, length, value in value:
                print('  {name}[{type_id}] ({length} B): {value!r}'.format(
                    name=name,
                    type_id=type_id,
                    length=length,
                    value=value,
                ))
        else:
            print('{name}[{type_id}] ({length} B): {value!r}'.format(
                name=name,
                type_id=type_id,
                length=length,
                value=value,
            ))

    return 0


if __name__ == '__main__':
    sys.exit(main())
