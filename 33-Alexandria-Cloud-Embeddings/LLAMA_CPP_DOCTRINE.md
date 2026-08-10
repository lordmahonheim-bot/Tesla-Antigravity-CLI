![Status](https://img.shields.io/badge/Status-MVP-blue) ![Ecosystem](https://img.shields.io/badge/Ecosystem-TESLA%20ANTIGRAVITY-purple) ![Security](https://img.shields.io/badge/Security-ID%20LOCKED-red) ![Python](https://img.shields.io/badge/Python-3.12+-blue)

# llama.cpp Doctrine — Strictly Ephemeral Tooling Usage

Under the Vigilum Codex doctrine and to preserve the hardware stability of MIDGARD (8 GB RAM, CPU-only):

## 1. Absolute Prohibition of Resident Inference
*   It is strictly forbidden to load inference models into RAM permanently.
*   Running persistent daemon processes such as `llama-server` is prohibited.
*   Using interactive tools like `llama-cli` in inference mode is prohibited.
*   Importing libraries that link the Python interpreter to inference runtimes (such as `llama-cpp-python`) is strictly forbidden in production scripts.

## 2. Permitted Usage Scope (Tooling)
The use of the `llama.cpp` software suite is exclusively restricted to model preparation and optimization tasks:
*   Converting native formats (e.g., HuggingFace) to the standardized GGUF format.
*   Quantizing (weight compression) to highly optimized compressed formats (types `Q4_K_M`, `Q5_K_M`, or `Q8_0`).
*   Splitting or merging GGUF files.

## 3. Ephemeral Isolation and Cleanup Pattern
Every tooling task must comply with the following hardware constraints:
1.  **Disk Space Check**: Ensure the system has at least 8 GB of free space on the target partition before starting.
2.  **Dedicated Temporary Folder**: All operations must take place in a disposable, isolated working directory under `/tmp/llama-pack-XXXXXX` (generated via `mktemp -d`).
3.  **Hermetic Subprocess Call**: The `llama-quantize` tool must be invoked as an ephemeral external process via Python's `subprocess.run` with explicit resource limits.
4.  **Physical Validation**: After writing the final quantized file, its integrity must be verified by checking for the GGUF file magic header (`0x46554747`, which is `GGUF` in ASCII).
5.  **Unconditional Purge**: A cleanup routine (like `trap EXIT` in bash or a Python `finally` block) must completely destroy the `/tmp/llama-pack-*` temporary folder after execution, regardless of success or failure.

---
*Canonical doctrine record certified on MIDGARD by Tesla Curator Prime.*
