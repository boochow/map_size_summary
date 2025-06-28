# map_size_summary

This Python script parses a linker map file and summarizes code and data sizes in a format similar to the Unix `size` tool.

## Features

* **Per-object breakdown** (`-l` option): Lists each `.o` file or archive member in the map, showing `.text`, `.data`, and `.bss` sizes and a total per entry.
* **Library-level aggregation** (default): When `-l` is not used, groups objects by their parent library (`.a`) and displays combined sizes for all members in each archive.
* Handles both single-line (`.section 0xADDR 0xSIZE filepath.o`) and split-line (long section name on one line, followed by address/size/filename on the next) entries.

## Usage

```bash
# Individual per-object summary (functions or archive members)
./map_size_summary.py -l <map-file-path>

# Library-level summary (aggregate all members of each .a)
./map_size_summary.py <map-file-path>
```

Output columns: `text`, `data`, `bss`, `total`, `filename`, followed by a final line showing overall totals.

## Requirements

* Python 3.x
* Standard library modules: `re`, `os`, `sys`, `collections`

No external dependencies.

## Example

without `-l` option:
```
    text   rodata     data      bss    total filename
    1406      156        0        0     1562 HeavyContext.o
    4894      216        0        0     5110 Heavy_tong_logue.o
    1132        0        0        0     1132 HvControlBinop.o
     136        6        0        0      142 HvControlCast.o
      66        0        0        0       66 HvControlIf.o
     306        0        0        0      306 HvControlPack.o
     198        0        0        0      198 HvControlSlice.o
     316       76        0        0      392 HvControlSystem.o
    1304        0        0        0     1304 HvControlUnop.o
     198        0        0        0      198 HvControlVar.o
    1216        0        0        0     1216 HvHeavy.o
     216        0        0        0      216 HvLightPipe.o
    1008       16        0        0     1024 HvMessage.o
     292        0        0        0      292 HvMessagePool.o
     526        0        0        0      526 HvMessageQueue.o
      12        0        0        0       12 HvSignalCPole.o
      40        6        0        0       46 HvSignalDel1.o
      54        0        0        0       54 HvSignalVar.o
     388       14        0        0      402 HvTable.o
     108        0        0        0      108 HvUtils.o
      96        0        0        0       96 _unit.o
    3784        4     2108       52     5948 libg.a
    2436        0        0        0     2436 libgcc.a
    6692       73        1        0     6766 libm.a
     560        0        0       36      596 logue_heavy.o
      32        0        0     3108     3140 logue_mem.o
   27416      567     2109     3196    33288 (TOTALS)
```

with `-l` option:
```
    text   rodata     data      bss    total filename
    1406      156        0        0     1562 HeavyContext.o
    4894      216        0        0     5110 Heavy_tong_logue.o
    1132        0        0        0     1132 HvControlBinop.o
     136        6        0        0      142 HvControlCast.o
      66        0        0        0       66 HvControlIf.o
     306        0        0        0      306 HvControlPack.o
     198        0        0        0      198 HvControlSlice.o
     316       76        0        0      392 HvControlSystem.o
    1304        0        0        0     1304 HvControlUnop.o
     198        0        0        0      198 HvControlVar.o
    1216        0        0        0     1216 HvHeavy.o
     216        0        0        0      216 HvLightPipe.o
    1008       16        0        0     1024 HvMessage.o
     292        0        0        0      292 HvMessagePool.o
     526        0        0        0      526 HvMessageQueue.o
      12        0        0        0       12 HvSignalCPole.o
      40        6        0        0       46 HvSignalDel1.o
      54        0        0        0       54 HvSignalVar.o
     388       14        0        0      402 HvTable.o
     108        0        0        0      108 HvUtils.o
      96        0        0        0       96 _unit.o
      12        0        0        0       12 libg.a(lib_a-errno.o)
     620        0        0        0      620 libg.a(lib_a-freer.o)
       0        4     1068        0     1072 libg.a(lib_a-impure.o)
      32        0        0        0       32 libg.a(lib_a-malloc.o)
    1392        0     1040       52     2484 libg.a(lib_a-mallocr.o)
     308        0        0        0      308 libg.a(lib_a-memcpy.o)
     156        0        0        0      156 libg.a(lib_a-memset.o)
       8        0        0        0        8 libg.a(lib_a-mlock.o)
     164        0        0        0      164 libg.a(lib_a-reent.o)
      36        0        0        0       36 libg.a(lib_a-sbrkr.o)
     732        0        0        0      732 libg.a(lib_a-strcmp.o)
     220        0        0        0      220 libg.a(lib_a-strlen.o)
     104        0        0        0      104 libg.a(lib_a-strncpy.o)
     880        0        0        0      880 libgcc.a(_arm_addsubdf3.o)
     272        0        0        0      272 libgcc.a(_arm_cmpdf2.o)
      64        0        0        0       64 libgcc.a(_arm_fixunsdfsi.o)
    1060        0        0        0     1060 libgcc.a(_arm_muldivdf3.o)
     160        0        0        0      160 libgcc.a(_arm_truncdfsf2.o)
     580        0        0        0      580 libm.a(lib_a-ef_acos.o)
     184        0        0        0      184 libm.a(lib_a-ef_acosh.o)
     504        0        0        0      504 libm.a(lib_a-ef_asin.o)
     176        0        0        0      176 libm.a(lib_a-ef_atanh.o)
     212        0        0        0      212 libm.a(lib_a-ef_cosh.o)
     432       24        0        0      456 libm.a(lib_a-ef_exp.o)
     536        0        0        0      536 libm.a(lib_a-ef_log.o)
     252        0        0        0      252 libm.a(lib_a-ef_sinh.o)
     164        0        0        0      164 libm.a(lib_a-ef_sqrt.o)
      88        0        0        0       88 libm.a(lib_a-s_fmax.o)
      92        0        0        0       92 libm.a(lib_a-s_fpclassify.o)
       0        0        1        0        1 libm.a(lib_a-s_lib_ver.o)
       4        0        0        0        4 libm.a(lib_a-s_matherr.o)
      16        0        0        0       16 libm.a(lib_a-s_nan.o)
     212        0        0        0      212 libm.a(lib_a-sf_asinh.o)
     140        0        0        0      140 libm.a(lib_a-sf_ceil.o)
     628        0        0        0      628 libm.a(lib_a-sf_expm1.o)
      16        0        0        0       16 libm.a(lib_a-sf_fabs.o)
      20        0        0        0       20 libm.a(lib_a-sf_finite.o)
     144        0        0        0      144 libm.a(lib_a-sf_floor.o)
      60        0        0        0       60 libm.a(lib_a-sf_fmax.o)
      60        0        0        0       60 libm.a(lib_a-sf_fmin.o)
      56        0        0        0       56 libm.a(lib_a-sf_fpclassify.o)
     568        0        0        0      568 libm.a(lib_a-sf_log1p.o)
     172        0        0        0      172 libm.a(lib_a-sf_tanh.o)
     192        9        0        0      201 libm.a(lib_a-wf_acos.o)
     172        7        0        0      179 libm.a(lib_a-wf_acosh.o)
     192        6        0        0      198 libm.a(lib_a-wf_asin.o)
     228        7        0        0      235 libm.a(lib_a-wf_atanh.o)
     208        6        0        0      214 libm.a(lib_a-wf_cosh.o)
     212        6        0        0      218 libm.a(lib_a-wf_sinh.o)
     172        8        0        0      180 libm.a(lib_a-wf_sqrt.o)
     560        0        0       36      596 logue_heavy.o
      32        0        0     3108     3140 logue_mem.o
   27416      567     2109     3196    33288 (TOTALS)
```

Functions defined:

* `parse_map_file(map_filepath)` → returns a dictionary mapping each object (or archive member) to its `{ 'text': size, 'data': size, 'bss': size }`.
* `print_size_like(per_object, list_individual, return_string=False)` → prints the size table. Pass `list_individual=True` for per-object output, or `False` to aggregate by library. If `return_string=True`, the output string is returned istead of being printed.

## License

MIT License
