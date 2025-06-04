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
      text       data        bss      total filename
      1406          0          0       1406 HeavyContext.o
      3714          0          0       3714 Heavy_Pluck.o
      1132          0          0       1132 HvControlBinop.o
       136          0          0        136 HvControlCast.o
       312          0          0        312 HvControlDelay.o
       198          0          0        198 HvControlSlice.o
       316          0          0        316 HvControlSystem.o
        96          0          0         96 HvControlTabhead.o
       198          0          0        198 HvControlVar.o
      1216          0          0       1216 HvHeavy.o
       216          0          0        216 HvLightPipe.o
      1008          0          0       1008 HvMessage.o
       292          0          0        292 HvMessagePool.o
       526          0          0        526 HvMessageQueue.o
       340          0          0        340 HvSignalPhasor.o
       288          0          0        288 HvSignalTabread.o
       164          0          0        164 HvSignalTabwrite.o
        54          0          0         54 HvSignalVar.o
       388          0          0        388 HvTable.o
       108          0          0        108 HvUtils.o
        96          0          0         96 _unit.o
      3784       2108         52       5944 libg.a
      2516          0          0       2516 libgcc.a
       496          0          0        496 libm.a
       588          0         32        620 logue_heavy.o
        32          0      10376      10408 logue_mem.o
     19620       2108      10460      32188 (TOTALS)
```

with `-l` option:
```
      text       data        bss      total filename
      1406          0          0       1406 HeavyContext.o
      3714          0          0       3714 Heavy_Pluck.o
      1132          0          0       1132 HvControlBinop.o
       136          0          0        136 HvControlCast.o
       312          0          0        312 HvControlDelay.o
       198          0          0        198 HvControlSlice.o
       316          0          0        316 HvControlSystem.o
        96          0          0         96 HvControlTabhead.o
       198          0          0        198 HvControlVar.o
      1216          0          0       1216 HvHeavy.o
       216          0          0        216 HvLightPipe.o
      1008          0          0       1008 HvMessage.o
       292          0          0        292 HvMessagePool.o
       526          0          0        526 HvMessageQueue.o
       340          0          0        340 HvSignalPhasor.o
       288          0          0        288 HvSignalTabread.o
       164          0          0        164 HvSignalTabwrite.o
        54          0          0         54 HvSignalVar.o
       388          0          0        388 HvTable.o
       108          0          0        108 HvUtils.o
        96          0          0         96 _unit.o
        12          0          0         12 libg.a(lib_a-errno.o)
       620          0          0        620 libg.a(lib_a-freer.o)
         0       1068          0       1068 libg.a(lib_a-impure.o)
        32          0          0         32 libg.a(lib_a-malloc.o)
      1392       1040         52       2484 libg.a(lib_a-mallocr.o)
       308          0          0        308 libg.a(lib_a-memcpy.o)
       156          0          0        156 libg.a(lib_a-memset.o)
         8          0          0          8 libg.a(lib_a-mlock.o)
       164          0          0        164 libg.a(lib_a-reent.o)
        36          0          0         36 libg.a(lib_a-sbrkr.o)
       732          0          0        732 libg.a(lib_a-strcmp.o)
       220          0          0        220 libg.a(lib_a-strlen.o)
       104          0          0        104 libg.a(lib_a-strncpy.o)
       880          0          0        880 libgcc.a(_arm_addsubdf3.o)
       272          0          0        272 libgcc.a(_arm_cmpdf2.o)
        80          0          0         80 libgcc.a(_arm_fixdfsi.o)
        64          0          0         64 libgcc.a(_arm_fixunsdfsi.o)
      1060          0          0       1060 libgcc.a(_arm_muldivdf3.o)
       160          0          0        160 libgcc.a(_arm_truncdfsf2.o)
        88          0          0         88 libm.a(lib_a-s_fmax.o)
        92          0          0         92 libm.a(lib_a-s_fpclassify.o)
       140          0          0        140 libm.a(lib_a-sf_ceil.o)
        60          0          0         60 libm.a(lib_a-sf_fmax.o)
        60          0          0         60 libm.a(lib_a-sf_fmin.o)
        56          0          0         56 libm.a(lib_a-sf_fpclassify.o)
       588          0         32        620 logue_heavy.o
        32          0      10376      10408 logue_mem.o
     19620       2108      10460      32188 (TOTALS)
```

Functions defined:

* `parse_map_file(map_filepath)` → returns a dictionary mapping each object (or archive member) to its `{ 'text': size, 'data': size, 'bss': size }`.
* `print_size_like(per_object, list_individual)` → prints the size table. Pass `list_individual=True` for per-object output, or `False` to aggregate by library.

## License

MIT License
