#!/usr/bin/env python3
import sys
import os
import re
from collections import defaultdict

def parse_map_file(map_filepath):
    """
    Parse a map file and aggregate per-object sizes for .text, .data, .bss,
    handling both single-line and split-line section definitions.
    Returns a dict: object_name -> { 'text': size, 'data': size, 'bss': size }
    """

    # Mapping from rules.ld output sections to regex patterns for input section names
    section_patterns = {
        'text': [r'^\.text(\..*)?$', r'^\.glue_7$', r'^\.glue_7t$', r'^\.gcc.*$'],
        'data': [r'^\.data(\..*)?$'],
        'bss':  [r'^\.bss(\..*)?$']
    }
    compiled_patterns = {
        sec: [re.compile(p) for p in pats]
        for sec, pats in section_patterns.items()
    }

    # Pattern for lines where section + address + size + filepath appear on one line:
    combined_line_pattern = re.compile(
        r'^\s*\.(?P<section>[A-Za-z0-9_\.]+)\s+'   # ".text" or ".data.__malloc_av_"
        r'0x[0-9A-Fa-f]+\s+'                       # address (ignored)
        r'0x(?P<size>[0-9A-Fa-f]+)\s+'             # size (hex)
        r'(?P<filepath>.+?\.o\)?)\s*$'             # filepath ending with ".o" or ".o)"
    )

    # Pattern for a line with only section name (long names cause split)
    section_only_pattern = re.compile(r'^\s*\.(?P<section>[A-Za-z0-9_\.]+)\s*$')

    # Pattern for next line containing address + size + filepath
    next_line_pattern = re.compile(
        r'^\s*0x[0-9A-Fa-f]+\s+0x(?P<size>[0-9A-Fa-f]+)\s+(?P<filepath>.+?\.o\)?)'
    )

    per_object = defaultdict(lambda: defaultdict(int))
    current_section = None

    with open(map_filepath, 'r') as f:
        for line in f:
            # 1) Combined single-line pattern
            m_comb = combined_line_pattern.match(line)
            if m_comb:
                sec_full = m_comb.group('section')
                size = int(m_comb.group('size'), 16)
                full_path = m_comb.group('filepath').strip()
                basename = os.path.basename(full_path)
                obj_key = re.search(r'[^/]+\.o\)?$', basename).group(0)

                # Determine which output section matches
                for out_sec, pats in compiled_patterns.items():
                    for pat in pats:
                        if pat.match('.' + sec_full):
                            key = 'data' if (out_sec == 'data' and sec_full.startswith('data.')) else out_sec
                            per_object[obj_key][key] += size
                            break
                    else:
                        continue
                    break

                current_section = None
                continue

            # 2) Section-only line
            m_sec = section_only_pattern.match(line)
            if m_sec:
                current_section = m_sec.group('section')
                continue

            # 3) Next-line data for section-only
            if current_section:
                m_next = next_line_pattern.match(line)
                if m_next:
                    size = int(m_next.group('size'), 16)
                    full_path = m_next.group('filepath').strip()
                    basename = os.path.basename(full_path)
                    obj_key = re.search(r'[^/]+\.o\)?$', basename).group(0)

                    sec_full = current_section
                    for out_sec, pats in compiled_patterns.items():
                        for pat in pats:
                            if pat.match('.' + sec_full):
                                key = 'data' if (out_sec == 'data' and sec_full.startswith('data.')) else out_sec
                                per_object[obj_key][key] += size
                                break
                        else:
                            continue
                        break

                    current_section = None
                continue

            # Otherwise ignore
    return per_object

def print_size_like(per_object, list_individual):
    """
    Print size summary in 'size' command format. If list_individual is True,
    show per-object entries. Otherwise, aggregate per library (.a) unit.
    """
    # Header
    print(f"{'text':>10} {'data':>10} {'bss':>10} {'total':>10} filename")
    total_text = total_data = total_bss = 0

    if list_individual:
        for obj_key in sorted(per_object.keys()):
            text_sz = per_object[obj_key].get('text', 0)
            data_sz = per_object[obj_key].get('data', 0)
            bss_sz = per_object[obj_key].get('bss', 0)
            total_sz = text_sz + data_sz + bss_sz

            total_text += text_sz
            total_data += data_sz
            total_bss += bss_sz

            print(f"{text_sz:10d} {data_sz:10d} {bss_sz:10d} {total_sz:10d} {obj_key}")
    else:
        # Aggregate by library or standalone object
        lib_agg = defaultdict(lambda: defaultdict(int))
        for obj_key, sizes in per_object.items():
            m = re.match(r'(.+\.a)\(.+\)', obj_key)
            if m:
                lib_name = m.group(1)
            else:
                lib_name = obj_key
            lib_agg[lib_name]['text'] += sizes.get('text', 0)
            lib_agg[lib_name]['data'] += sizes.get('data', 0)
            lib_agg[lib_name]['bss']  += sizes.get('bss', 0)

        for lib_key in sorted(lib_agg.keys()):
            text_sz = lib_agg[lib_key].get('text', 0)
            data_sz = lib_agg[lib_key].get('data', 0)
            bss_sz = lib_agg[lib_key].get('bss', 0)
            total_sz = text_sz + data_sz + bss_sz

            total_text += text_sz
            total_data += data_sz
            total_bss += bss_sz

            print(f"{text_sz:10d} {data_sz:10d} {bss_sz:10d} {total_sz:10d} {lib_key}")

    overall_total = total_text + total_data + total_bss
    print(f"{total_text:10d} {total_data:10d} {total_bss:10d} {overall_total:10d} (TOTALS)")

if __name__ == "__main__":
    # Parse arguments
    list_individual = False
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} [-l] <map-file-path>")
        sys.exit(1)

    if args[0] == '-l':
        list_individual = True
        args = args[1:]

    if len(args) != 1:
        print(f"Usage: {sys.argv[0]} [-l] <map-file-path>")
        sys.exit(1)

    map_filepath = args[0]
    if not os.path.isfile(map_filepath):
        print(f"Error: File '{map_filepath}' not found.")
        sys.exit(1)

    per_object = parse_map_file(map_filepath)
    print_size_like(per_object, list_individual)
