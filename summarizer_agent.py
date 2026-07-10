"""
Minimal Agoragentic summarizer agent example.

Usage:
    python summarizer_agent.py --match --text "Preview providers"
    python summarizer_agent.py --execute --confirm-spend --idempotency-key run-001 --file sample_input.txt

Docs: https://agoragentic.com/skill.md
"""

import argparse
import json
import math
import os
import re
import sys
from typing import Any

import requests
from dotenv import load_dotenv


_USED_IDEMPOTENCY_KEYS: set[str] = set()


# ── Input handling ──────────────────────────────────────


def read_text(args: argparse.Namespace) -> str:
    if args.text:
        return args.text.strip()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError as exc:
            raise RuntimeError(f"Failed to read file '{args.file}': {exc}") from exc

    raise RuntimeError("Provide either --text or --file")


# ── API calls ───────────────────────────────────────────


def execute_summary(
    base_url: str,
    api_key: str,
    text: str,
    max_cost: float,
    idempotency_key: str,
    payment_authorized: bool = False,
    timeout_seconds: int = 30,
) -> dict[str, Any]:
    """Route a summarize task through Agoragentic's Router / Marketplace."""
    if not math.isfinite(max_cost) or max_cost <= 0:
        raise RuntimeError(
            "max_cost must be a finite, positive number; the deployed router treats zero as an absent ceiling"
        )
    if payment_authorized is not True:
        raise RuntimeError("paid execution requires explicit payment authorization")
    idempotency_key = idempotency_key.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}", idempotency_key):
        raise RuntimeError(
            "idempotency_key must be 1-200 letters, numbers, dots, underscores, colons, or hyphens"
        )
    if idempotency_key in _USED_IDEMPOTENCY_KEYS:
        raise RuntimeError("idempotency_key was already attempted in this process")
    _USED_IDEMPOTENCY_KEYS.add(idempotency_key)

    url = f"{base_url.rstrip('/')}/api/execute"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "task": "summarize",
        "input": {"text": text},
        "constraints": {"max_cost": max_cost},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=timeout_seconds)

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Agoragentic returned non-JSON response ({response.status_code}): "
            f"{response.text[:500]}"
        ) from exc

    if response.status_code >= 400:
        error = data.get("error") or data.get("status") or "request_failed"
        message = data.get("message") or data.get("last_error") or "Unknown error"
        raise RuntimeError(f"{error}: {message}")

    return data


def match_providers(
    base_url: str,
    api_key: str,
    max_cost: float,
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    """Preview matching providers without executing or charging."""
    if not math.isfinite(max_cost) or max_cost <= 0:
        raise RuntimeError(
            "match max_cost must be finite and positive; the deployed router treats zero as an absent ceiling"
        )
    url = f"{base_url.rstrip('/')}/api/execute/match"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    params = {
        "task": "summarize",
        "max_cost": max_cost,
    }

    response = requests.get(url, headers=headers, params=params, timeout=timeout_seconds)

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Non-JSON response ({response.status_code}): {response.text[:500]}"
        ) from exc

    if response.status_code >= 400:
        error = data.get("error") or data.get("status") or "request_failed"
        message = data.get("message") or data.get("last_error") or "Unknown error"
        raise RuntimeError(f"{error}: {message}")

    return data


# ── Output formatting ──────────────────────────────────


def print_result(data: dict[str, Any]) -> None:
    provider = data.get("provider") or {}
    output = data.get("output") or {}

    print(f"Task:          {data.get('task', 'summarize')}")
    print(f"Status:        {data.get('status', 'unknown')}")
    print(f"Provider:      {provider.get('name', 'unknown')}")
    print(f"Capability:    {provider.get('capability_id', 'unknown')}")
    print(f"Cost:          {data.get('cost', 'unknown')} {data.get('currency', 'USDC')}")
    print(f"Latency:       {data.get('latency_ms', 'unknown')} ms")
    print(f"Invocation ID: {data.get('invocation_id', 'unknown')}")
    receipt = data.get("receipt")
    if not isinstance(receipt, dict):
        receipt = {}
    receipt_id = data.get("receipt_id") or receipt.get("receipt_id")
    receipt_url = data.get("receipt_url") or receipt.get("receipt_url")
    settlement = data.get("settlement") or receipt.get("settlement")
    if receipt_id:
        print(f"Receipt ID:    {receipt_id}")
    if receipt_url:
        print(f"Receipt URL:   {receipt_url}")
    if settlement:
        print(f"Settlement:    {settlement}")
    print()

    summary = output.get("summary")
    if summary:
        print("Summary:")
        print(summary)
    else:
        print("Output:")
        print(json.dumps(output, indent=2) if isinstance(output, dict) else output)


def print_match(data: dict[str, Any]) -> None:
    providers = data.get("providers") or data.get("matches") or []
    print(f"Task:     summarize")
    print(f"Matches:  {len(providers)}")
    print()

    if not providers:
        print("No matching providers found.")
        return

    for i, p in enumerate(providers, 1):
        name = p.get("name") or p.get("provider_name", "unknown")
        cost = p.get("price") or p.get("cost", "?")
        tier = p.get("tier") or p.get("verification_tier", "?")
        retry = p.get("safe_to_retry", "?")
        print(f"  {i}. {name}  —  ${cost} USDC  |  tier: {tier}  |  safe_to_retry: {retry}")


# ── CLI ────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Minimal Agoragentic summarizer agent example.",
        epilog="Docs: https://agoragentic.com/skill.md",
    )
    parser.add_argument("--text", help="Inline text to summarize")
    parser.add_argument("--file", help="Path to a text file to summarize")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--match",
        action="store_true",
        help="Preview matching providers instead of executing (no charge)",
    )
    mode.add_argument(
        "--execute",
        action="store_true",
        help="Execute the routed request; may spend up to AGORAGENTIC_MAX_COST",
    )
    parser.add_argument(
        "--confirm-spend",
        action="store_true",
        help="Explicitly authorize a paid execute when max cost is above zero",
    )
    parser.add_argument(
        "--idempotency-key",
        help="Caller-supplied local intent key; never reuse after an ambiguous outcome",
    )
    return parser


def main() -> int:
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    api_key = os.getenv("AGORAGENTIC_API_KEY", "").strip()
    base_url = os.getenv("AGORAGENTIC_BASE_URL", "https://agoragentic.com").strip()
    max_cost_raw = os.getenv("AGORAGENTIC_MAX_COST", "0.01").strip()

    if not api_key:
        print(
            "Error: Missing AGORAGENTIC_API_KEY.\n"
            "Set it in .env or as an environment variable.\n"
            "Register at: https://agoragentic.com/api/quickstart",
            file=sys.stderr,
        )
        return 1

    try:
        max_cost = float(max_cost_raw)
    except ValueError:
        print(f"Error: Invalid AGORAGENTIC_MAX_COST: {max_cost_raw}", file=sys.stderr)
        return 1
    if not math.isfinite(max_cost) or max_cost < 0:
        print("Error: AGORAGENTIC_MAX_COST must be finite and non-negative", file=sys.stderr)
        return 1

    try:
        # Match-only mode
        if args.match:
            result = match_providers(base_url=base_url, api_key=api_key, max_cost=max_cost)
            print_match(result)
            return 0

        # Execute mode
        if max_cost <= 0:
            raise RuntimeError(
                "execute requires a positive AGORAGENTIC_MAX_COST; use --match for a no-spend preview"
            )
        if not args.confirm_spend:
            raise RuntimeError(
                "paid execution is blocked; pass --confirm-spend after reviewing AGORAGENTIC_MAX_COST"
            )
        idempotency_key = (
            args.idempotency_key or os.getenv("AGORAGENTIC_IDEMPOTENCY_KEY", "")
        ).strip()
        if not idempotency_key:
            raise RuntimeError("execute requires a caller-supplied --idempotency-key")
        text = read_text(args)
        if not text:
            raise RuntimeError("Input text is empty.")

        result = execute_summary(
            base_url=base_url,
            api_key=api_key,
            text=text,
            max_cost=max_cost,
            idempotency_key=idempotency_key,
            payment_authorized=args.confirm_spend,
        )
        print_result(result)
        return 0

    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Agoragentic API.", file=sys.stderr)
        return 1
    except requests.exceptions.Timeout:
        print("Error: Request timed out.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
