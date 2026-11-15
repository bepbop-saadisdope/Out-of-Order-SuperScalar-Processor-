# Out-of-Order Superscalar Processor: Design-Space Exploration

Computer Architecture (BCS-5F, Fall 2026), FAST-NUCES Lahore.
Project: design-space exploration with SimpleScalar `sim-outorder` on SPEC95 benchmarks.

- Group: 13
- Benchmarks (group 13, (13-1) mod 6 = 0): `anagram` and `go`
- Runs in Parts 2-6 are capped with `-max:inst 100000000`

## Repository layout

| Path | Contents |
|---|---|
| `simplesim-3.0/` | SimpleScalar 3.0 source (vendored; patched for modern glibc by `build.sh`) |
| `bench/Programs/` | `anagram.ss`, `go.ss` (little-endian PISA binaries) |
| `bench/Input/` | `words`, `anagram.in`, `2stone9.in` |
| `bench/Expected_Output/` | `anagram.out`, `go.out` (reference outputs) |
| `build.sh` | Applies the `termio.h` to `termios.h` patch and builds `sim-outorder` with `-O2` |
| `lib.sh` | `run <bench> <tag> [options]` helper; finds all paths relative to itself |
| `partN.sh` | Batch script for project part N |
| `results/` | Raw `-redir:sim` stats (`<bench>_<tag>.txt`) and program output (`.out`), unedited |

## Reproduce

Requires Linux, gcc and make.

    bash build.sh        # builds simplesim-3.0/sim-outorder (about 20 s)
    bash part1.sh        # full baseline runs (go takes tens of minutes)

Verify that the simulated programs give the correct output:

    diff results/anagram_P1_default.out bench/Expected_Output/anagram.out
    diff results/go_P1_default.out bench/Expected_Output/go.out

Every run is named `<bench>_<tag>.txt`; the tag identifies the configuration
(for example `P2_W4_io` = Part 2, width 4, in-order). `run` skips runs whose output
already exists, so an interrupted script can simply be rerun.

## Progress

| Part | Topic | Status |
|---|---|---|
| 1 | Baseline, verification, instruction mix | not run yet |
| 2 | Width and in-order vs out-of-order | pending |
| 3 | RUU size | pending |
| 4 | Memory hierarchy | pending |
| 5 | Branch prediction | pending |
| 6 | Custom design under budget | pending |

## Notes

- The simulator is run through `env -i` to avoid the "environment overflow" error.
- Build artifacts (`*.o`, `sim-outorder`, `sysprobe`, `*.a`) are not committed; `build.sh` recreates them.

## Credits

- SimpleScalar 3.0 by Todd Austin: https://github.com/toddmaustin/simplesim-3.0
- SPEC95 PISA binaries and inputs: https://github.com/priyankarroychowdhury3/Simplescalar
