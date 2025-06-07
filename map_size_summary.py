#!/usr/bin/env python3
import sys
import os
import re
from collections import defaultdict

def parse_map_file(map_filepath):
    """
    Parse a map file and aggregate per-object sizes for .text, .rodata, .data, .bss,
    handling both single-line and split-line section definitions.
    Returns a dict: object_name -> { 'text': size, 'rodata': size, 'data': size, 'bss': size }
    """

    # Mapping from rules.ld output sections to regex patterns for input section names
    section_patterns = {
        'text':   [r'^\.text(\..*)?$', r'^\.glue_7$', r'^\.glue_7t$', r'^\.gcc.*$'],
        'rodata': [r'^\.rodata(\..*)?$'],
        'data':   [r'^\.data(\..*)?$'],
        'bss':    [r'^\.bss(\..*)?$']
    }
    compiled_patterns = {
        sec: [re.compile(p) for p in pats]
        for sec, pats in section_patterns.items()
    }

    # Pattern for lines where section + address + size + filepath appear on one line:
    combined_line_pattern = re.compile(
        r'^\s*\.(?P<section>[A-Za-z0-9_\.]+)\s+'   # ".text" or long section
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
            # Combined single-line entry
            m_comb = combined_line_pattern.match(line)
            if m_comb:
                sec_full = m_comb.group('section')
                size = int(m_comb.group('size'), 16)
                filepath = m_comb.group('filepath').strip()
                basename = os.path.basename(filepath)
                obj_key = re.search(r'[^/]+\.o\)?$', basename).group(0)

                # Match into text/rodata/data/bss
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

            # Section-only line
            m_sec = section_only_pattern.match(line)
            if m_sec:
                current_section = m_sec.group('section')
                continue

            # Next-line data for split section
            if current_section:
                m_next = next_line_pattern.match(line)
                if m_next:
                    size = int(m_next.group('size'), 16)
                    filepath = m_next.group('filepath').strip()
                    basename = os.path.basename(filepath)
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

    return per_object

def print_size_like(per_object, list_individual, return_string=False):
    """
    Print or return size summary in 'size' command format.
    Columns: text, rodata, data, bss, total, filename.
    If list_individual=True, list per-object; else aggregate per library.
    If return_string=True, return the output string instead of printing.
    """
    lines = []
    header = f"{'text':>8} {'rodata':>8} {'data':>8} {'bss':>8} {'total':>8} filename"
    lines.append(header)
    total_text = total_rodata = total_data = total_bss = 0

    def append_line(key, sizes):
        nonlocal total_text, total_rodata, total_data, total_bss
        t = sizes.get('text', 0)
        r = sizes.get('rodata', 0)
        d = sizes.get('data', 0)
        b = sizes.get('bss', 0)
        total = t + r + d + b
        total_text += t; total_rodata += r; total_data += d; total_bss += b
        lines.append(f"{t:8d} {r:8d} {d:8d} {b:8d} {total:8d} {key}")

    if list_individual:
        for key in sorted(per_object.keys()):
            append_line(key, per_object[key])
    else:
        lib_agg = defaultdict(lambda: defaultdict(int))
        for key, sizes in per_object.items():
            m = re.match(r'(.+\.a)\(.+\)', key)
            lib = m.group(1) if m else key
            lib_agg[lib]['text']   += sizes.get('text', 0)
            lib_agg[lib]['rodata'] += sizes.get('rodata', 0)
            lib_agg[lib]['data']   += sizes.get('data', 0)
            lib_agg[lib]['bss']    += sizes.get('bss', 0)
        for lib in sorted(lib_agg.keys()):
            append_line(lib, lib_agg[lib])

    overall = total_text + total_rodata + total_data + total_bss
    totals_line = f"{total_text:8d} {total_rodata:8d} {total_data:8d} {total_bss:8d} {overall:8d} (TOTALS)"
    lines.append(totals_line)

    output = "\n".join(lines)
    if return_string:
        return output
    print(output)

if __name__ == "__main__":
    args = sys.argv[1:]
    list_individual = False
    if args and args[0] == '-l':
        list_individual = True
        args = args[1:]
    if len(args) != 1:
        print(f"Usage: {sys.argv[0]} [-l] <map-file-path>")
        sys.exit(1)
    path = args[0]
    if not os.path.isfile(path):
        print(f"Error: File '{path}' not found.")
        sys.exit(1)

    per_obj = parse_map_file(path)
    print_size_like(per_obj, list_individual)
