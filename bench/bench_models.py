#!/usr/bin/env python3
"""
bench_models.py — small local benchmark for comparing Ollama model speed.

Goal
----
Provide a *fair-ish* comparison between models on the same machine by:
- using the same prompt
- limiting output length (approx) by requesting short answers
- doing both cold-ish and warm runs
- measuring wall-clock time

Notes
-----
- This measures end-to-end latency of `ollama run <model> <prompt>`.
  It is not a precise tokens/sec benchmark, but it is practical and stable.
- The "cold" run may still be warm if the model was already loaded by Ollama.
- On CPU-only machines, model load + first token latency can dominate.

Usage
-----
  python3 bench/bench_models.py

Optional flags:
  python3 bench/bench_models.py --models tinyllama:latest gemma:2b llama3.2:1b
  python3 bench/bench_models.py --runs 3 --warmup 1 --timeout 180
  python3 bench/bench_models.py --prompt "Explain SSH risks in 1 sentence."

Requirements
------------
- Ollama installed and available in PATH as `ollama`
- Models pulled locally (e.g., `ollama pull llama3.2:1b`)
"""

from __future__ import annotations

import argparse
import statistics
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple


DEFAULT_MODELS = ["tinyllama:latest", "gemma:2b", "llama3.2:1b"]

DEFAULT_PROMPT = (
    "Answer in EXACTLY 1 sentence, max 20 words.\n"
    "Question: Give a concise summary of SSH security risks."
)


@dataclass(frozen=True)
class RunResult:
    model: str
    seconds: float
    exit_code: int
    stdout_chars: int
    stderr_chars: int
    stdout_preview: str
    error: Optional[str] = None


def run_ollama(model: str, prompt: str, timeout_s: int) -> RunResult:
    t0 = time.perf_counter()
    try:
        p = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        dt = time.perf_counter() - t0
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        preview = out.replace("\n", " ")[:160]
        return RunResult(
            model=model,
            seconds=dt,
            exit_code=p.returncode,
            stdout_chars=len(out),
            stderr_chars=len(err),
            stdout_preview=preview,
            error=None,
        )
    except subprocess.TimeoutExpired:
        dt = time.perf_counter() - t0
        return RunResult(
            model=model,
            seconds=dt,
            exit_code=124,
            stdout_chars=0,
            stderr_chars=0,
            stdout_preview="",
            error=f"timeout after {timeout_s}s",
        )
    except FileNotFoundError:
        return RunResult(
            model=model,
            seconds=0.0,
            exit_code=127,
            stdout_chars=0,
            stderr_chars=0,
            stdout_preview="",
            error="ollama not found in PATH",
        )


def summarize_times(times: List[float]) -> Tuple[float, float, float]:
    """
    Return (mean, median, stdev). stdev is 0.0 if <2 samples.
    """
    mean = statistics.mean(times)
    median = statistics.median(times)
    stdev = statistics.stdev(times) if len(times) >= 2 else 0.0
    return mean, median, stdev


def print_table(title: str, results: List[RunResult]) -> None:
    print(f"\n=== {title} ===")
    header = f"{'model':24} {'sec':>8} {'code':>5} {'out':>6}  preview"
    print(header)
    print("-" * len(header))
    for r in results:
        sec = f"{r.seconds:.2f}"
        outn = str(r.stdout_chars)
        code = str(r.exit_code)
        preview = r.stdout_preview
        if r.error:
            preview = f"[{r.error}] {preview}".strip()
        print(f"{r.model:24} {sec:>8} {code:>5} {outn:>6}  {preview}")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Benchmark Ollama model latency (practical wall-clock).")
    ap.add_argument(
        "--models",
        nargs="+",
        default=DEFAULT_MODELS,
        help="List of Ollama models to test (must be pulled already).",
    )
    ap.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="Prompt to run for each model (recommend short output constraint).",
    )
    ap.add_argument(
        "--warmup",
        type=int,
        default=1,
        help="Number of warmup runs per model (ignored in stats).",
    )
    ap.add_argument(
        "--runs",
        type=int,
        default=3,
        help="Number of measured runs per model.",
    )
    ap.add_argument(
        "--timeout",
        type=int,
        default=180,
        help="Timeout per run in seconds.",
    )
    args = ap.parse_args(argv)

    models: List[str] = list(args.models)
    prompt: str = str(args.prompt)
    warmup_n: int = int(args.warmup)
    runs_n: int = int(args.runs)
    timeout_s: int = int(args.timeout)

    if runs_n <= 0:
        print("ERROR: --runs must be >= 1", file=sys.stderr)
        return 2
    if warmup_n < 0:
        print("ERROR: --warmup must be >= 0", file=sys.stderr)
        return 2

    print("Ollama model benchmark")
    print(f"- models: {models}")
    print(f"- warmup runs/model: {warmup_n}")
    print(f"- measured runs/model: {runs_n}")
    print(f"- timeout/run: {timeout_s}s")
    print(f"- prompt (first 120 chars): {prompt[:120]!r}")

    # Warmup passes (to reduce load/compile noise)
    warmup_results: List[RunResult] = []
    if warmup_n:
        for m in models:
            for _ in range(warmup_n):
                warmup_results.append(run_ollama(m, prompt, timeout_s))
        print_table("Warmup (not included in stats)", warmup_results)

    # Measured passes
    measured: List[RunResult] = []
    for m in models:
        for _ in range(runs_n):
            measured.append(run_ollama(m, prompt, timeout_s))

    print_table("Measured runs", measured)

    # Stats per model
    print("\n=== Summary (measured) ===")
    print(f"{'model':24} {'mean':>8} {'median':>8} {'stdev':>8} {'ok/total':>9}")
    print("-" * 62)

    for m in models:
        rs = [r for r in measured if r.model == m]
        ok = [r for r in rs if r.exit_code == 0 and not r.error]
        times = [r.seconds for r in ok]
        if not times:
            print(f"{m:24} {'-':>8} {'-':>8} {'-':>8} {len(ok):>2}/{len(rs):<6}  (no successful runs)")
            continue
        mean, median, stdev = summarize_times(times)
        print(f"{m:24} {mean:>8.2f} {median:>8.2f} {stdev:>8.2f} {len(ok):>2}/{len(rs):<6}")

    # Quick recommendation: pick lowest median among successful runs.
    candidates = []
    for m in models:
        rs = [r for r in measured if r.model == m]
        ok = [r for r in rs if r.exit_code == 0 and not r.error]
        if ok:
            candidates.append((statistics.median([r.seconds for r in ok]), m))
    if candidates:
        candidates.sort()
        best_median, best_model = candidates[0]
        print(f"\nRecommended for speed (lowest median): {best_model} ({best_median:.2f}s)")
    else:
        print("\nNo successful runs; check that Ollama is running and models are pulled.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
