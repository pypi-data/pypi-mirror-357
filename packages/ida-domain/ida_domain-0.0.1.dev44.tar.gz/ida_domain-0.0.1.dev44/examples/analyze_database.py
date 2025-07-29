#!/usr/bin/env python3
"""
Database traversing example for IDA Domain API.

This example demonstrates how to traverse an IDA database and list entities.
"""

import argparse
import ida_domain


def traverse_database(db_path):
    """Iterate all entities  in the database and print basic information"""
    ida_options = ida_domain.Database.IdaCommandBuilder().auto_analysis(True).new_database(True)

    db = ida_domain.Database()
    if db.open(db_path, ida_options):
        print(f'Entry point: {hex(db.entry_point)}')

        print('Metadata:')
        for key, value in db.metadata.items():
            print(f' {key}: {value}')

        for f in db.functions.get_all():
            print(f'Function - name {f.name}, start ea {hex(f.start_ea)}, end ea {f.end_ea}')

        for s in db.segments.get_all():
            print(f'Segment - name {ida_segment.get_segm_name(s)}')  # noqa F821

        for t in db.types.get_all():
            if t.name is not None:
                print(f'Type - name {t.name}, id {t.get_tid()}')
            else:
                print(f'Type - id {t.get_tid()}')

        for c in db.comments.get_all(False):
            print(f'Comment - value {c}')

        for s1 in db.strings.get_all():
            print(f'String - value {s1}')

        for n in db.names.get_all():
            print(f'Name - value {n}')

        for b in db.basic_blocks.get_between(db.minimum_ea, db.maximum_ea):
            print(f'Basic block - start ea {hex(b.start_ea)}, end ea {hex(b.end_ea)}')

        for inst in db.instructions.get_between(db.minimum_ea, db.maximum_ea):
            dec = db.instructions.get_disassembly(inst)
            if dec:
                print(f'Instruction - ea {hex(inst.ea)}, asm {dec}')

        db.close(False)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description='Database traversing example')
    parser.add_argument(
        '-f', '--input-file', help='Binary input file to be loaded', type=str, required=True
    )
    args = parser.parse_args()
    traverse_database(args.input_file)


if __name__ == '__main__':
    main()
