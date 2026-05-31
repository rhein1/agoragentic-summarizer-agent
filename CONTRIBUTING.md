# Contributing

Keep this repository a minimal, safe Python summarizer example.

- Prefer `execute()` over hardcoded provider IDs.
- Keep `--match` as the no-charge preview path.
- Do not commit secrets, API keys, raw private payloads, wallet-private data, or raw receipts.
- Do not add deployment automation, public execute routes, x402 settlement mutation, marketplace publication, or provider-specific hidden credentials.
- Keep examples honest about what is live, optional, paid, or policy-gated.

Before submitting changes, run:

```bash
python -m py_compile summarizer_agent.py
```
