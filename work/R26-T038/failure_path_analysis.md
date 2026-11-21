# R26-T038: Roman-Numerals — Failure-Path Coverage & Actionable Error Design

## Overview
This document outlines the failure-path architecture for `utilities/Roman-Numerals/main.py`. The design guarantees:
1. **Actionable Error Messages:** Errors identify the invalid input, state the allowed bounds (`1..3999`), explain the historical/representational reason for rejection, and provide clear corrective action.
2. **Caller Data Invariance:** In-memory caller collections (`list`, `dict`) are never mutated or partially altered when conversion fails.
3. **Filesystem Transactional Safety:** Atomic file operations ensure target files are never created, truncated, or corrupted when file conversion fails.

---

## 1. Domain Constraints & Rejection Rationale

| Value / Range | Exception Type | Reason for Rejection | Actionable Guidance |
|:---:|:---:|:---|:---|
| `0` | `ValueError` | Zero was not represented in canonical Roman numerals (Romans used words like *nulla*). | "Action: Supply an integer within 1..3999." |
| `< 0` | `ValueError` | Negative quantities have no representation in Roman numeral notation. | "Action: Supply an integer within 1..3999." |
| `>= 4000` | `ValueError` | Standard subtractive notation terminates at `MMMCMXCIX` (3999). | "Action: Supply an integer within 1..3999." |
| `float`, `str`, `bool`, `None` | `TypeError` | Mathematical Roman numeral encoding requires integer values. | "Action: Convert or pass an integer value (e.g. to_roman(42))." |

---

## 2. Failure-Path Invariance Proofs

### A. Caller In-Memory Data Immutability
When `convert_many(numbers)` processes a batch:
- If an invalid element occurs at index $k$ (e.g. `0` at index 3 in `[1, 4, 9, 0, 58]`):
  - A `ValueError` is raised identifying the exact index and value.
  - The caller's input list remains bit-for-bit identical to its pre-call state:
    $$\text{numbers}_{\text{after}} \equiv \text{numbers}_{\text{before}}$$
- Tested in `test_caller_list_intact_on_batch_failure` and `test_caller_dict_and_complex_data_intact_on_failure`.

### B. Filesystem Atomic Rollback
When `convert_file(source_path, dest_path)` runs:
- Input validation runs strictly before modifying any persistent state.
- Output is written to a hidden temporary file (`.roman_tmp_*`) in the target directory.
- The destination file is only updated via an atomic filesystem rename (`Path.replace`).
- If an error occurs on any line:
  - If the target file did not exist, it is **never created**.
  - If the target file already existed, its prior contents remain **100% untouched**.
  - The temporary file is unlinked.
- Tested in `test_destination_file_not_created_on_failure` and `test_existing_destination_file_preserved_on_failure`.
