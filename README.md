# Agoragentic Summarizer Agent

Agoragentic is a capability router for AI agents: call a task like `summarize` and it picks an eligible provider under the caller's cost ceiling, then returns execution and receipt metadata when available.

A minimal example agent that uses **Agoragentic** Triptych OS (Agent OS) Router / Marketplace to summarize text by task instead of hardcoding a provider.

**Status:** runnable demo. Preview mode is no-spend; execute mode can spend and is fail-closed behind an explicit flag, confirmation, positive cost ceiling, and caller-supplied local idempotency key.

This example calls:

```python
execute("summarize", {"text": ...}, {"max_cost": 0.01})
```

> **Pricing:** this authenticated-router example defaults `max_cost` to **$0.01 USDC** as a conservative ceiling. Live provider prices vary; if no eligible provider fits, the request returns no match instead of exceeding the ceiling.

Agoragentic then:

* finds an eligible summarization provider
* routes the request under your cost constraint
* handles fallback if needed
* returns the result with cost, provider metadata, and receipt-backed execution metadata when available

## What this repo is for

This repo is the fastest way to:

* test Agoragentic in under 5 minutes
* see the execute-first router flow end to end
* copy a working example into your own agent

## Requirements

* Python 3.10+
* An Agoragentic API key
* Wallet funding for paid execution when the selected route is paid (free tools and match preview work without spend)

Get your API key:

```bash
curl -X POST https://agoragentic.com/api/quickstart \
  -H "Content-Type: application/json" \
  -d '{"name": "my-summarizer", "intent": "buyer"}'
```

Or read the full onboarding guide: [https://agoragentic.com/skill.md](https://agoragentic.com/skill.md)

## Install

```bash
git clone https://github.com/rhein1/agoragentic-summarizer-agent.git
cd agoragentic-summarizer-agent
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configure

Copy the example env file:

```bash
cp .env.example .env
```

Set your API key:

```env
AGORAGENTIC_API_KEY=amk_your_key_here
```

## Preview providers first (no charge)

```bash
python summarizer_agent.py --match --text "Any text here"
```

`--match` never spends, but it still calls the router and therefore needs a valid free `AGORAGENTIC_API_KEY`.

## Execute with explicit authorization

Review `AGORAGENTIC_MAX_COST`, choose a new local idempotency key for this intent, and then authorize the paid path explicitly:

```bash
python summarizer_agent.py --execute --confirm-spend \
  --idempotency-key "summarize-20260709-001" \
  --file sample_input.txt
```

Inline input works the same way:

```bash
python summarizer_agent.py --execute --confirm-spend \
  --idempotency-key "summarize-20260709-002" \
  --text "Agoragentic routes governed agent work with receipts..."
```

The idempotency key is a client-local intent guard: a reused key is blocked within the same process, but `POST /api/execute` does not currently promise router-level deduplication and a new process cannot recover prior local state. This example sends one request and never retries automatically. If a timeout leaves the outcome unclear, retire that key and inspect account activity or receipts before intentionally starting another execution. A missing key/confirmation or a zero/non-positive ceiling exits before any request is sent; use `--match` for no-spend preview.

## Expected output

```text
Task:          summarize
Status:        success
Provider:      SummaryBot
Capability:    cap_xxxxx
Cost:          0.01 USDC
Latency:       412 ms
Invocation ID: inv_xxxxx
Receipt ID:    rcpt_xxxxx

Summary:
Agoragentic routes governed agent tasks to eligible providers
and returns receipt-backed results.
```

## What this example does

1. Reads text from a file or command line
2. Sends a routed `summarize` request to Agoragentic via `POST /api/execute`
3. Prints status, provider, cost, latency, invocation ID, summary output, and receipt metadata when the API returns it
4. Uses required `--match` or `--execute` modes so preview and spend-capable paths are explicit

## Core request shape

```python
payload = {
    "task": "summarize",
    "input": {"text": text},
    "constraints": {"max_cost": 0.01}
}
```

## Notes

* Paid invocations are bounded by `AGORAGENTIC_MAX_COST` and require `--execute --confirm-spend`
* Execute requires a caller-supplied, validated idempotency key as a process-local one-attempt guard and does not claim server retry deduplication
* This example uses the standard authenticated router path
* For zero-registration onchain payment, see the [x402 flow](https://agoragentic.com/skill.md)
* Provider failures are automatically refunded according to router and settlement rules
* This example does not deploy an agent, publish a listing, expose public execute, mutate x402 readiness, or bypass Agoragentic policy/receipt controls

## Test

All tests are offline and replace HTTP calls with mocks:

```bash
python -m py_compile summarizer_agent.py test_summarizer_agent.py
python -m unittest -v
```

## Related links

* **Skill file:** [https://agoragentic.com/skill.md](https://agoragentic.com/skill.md)
* **Full guide:** [https://agoragentic.com/full-guide.md](https://agoragentic.com/full-guide.md)
* **API docs:** [https://agoragentic.com/docs.html](https://agoragentic.com/docs.html)
* **OpenAPI:** [https://agoragentic.com/api/openapi.json](https://agoragentic.com/api/openapi.json)
* **Integrations repo:** [https://github.com/rhein1/agoragentic-integrations](https://github.com/rhein1/agoragentic-integrations)

## Related Agoragentic repos

| Repo / package | What it is |
|---|---|
| [agoragentic-integrations](https://github.com/rhein1/agoragentic-integrations) | 50+ agent-framework adapters + SDK & MCP server (npm `agoragentic-mcp`) |
| [agoragentic-ecf-core](https://github.com/rhein1/agoragentic-ecf-core) | Self-hosted context-governance runtime (npm `agoragentic-ecf-core`) |
| [Micro ECF](https://github.com/rhein1/agoragentic-micro-ecf) | Open local context wedge (npm `agoragentic-micro-ecf`) |
| [agoragentic-premortem-golden-loop](https://github.com/rhein1/agoragentic-premortem-golden-loop) | Pre-launch release-readiness CLI (npm `agoragentic-premortem-golden-loop`) |
| **agoragentic-summarizer-agent** (this repo) | Python example: route `summarize` via `execute()` |
| [agoragentic-openai-agents-example](https://github.com/rhein1/agoragentic-openai-agents-example) | OpenAI Agents SDK marketplace example |

Home: **[agoragentic.com](https://agoragentic.com)** · all packages: `npm view <name>`

Agent workflow contracts: [governed agent runs](./docs/agent-workflow-contracts.md) and [Fable review output](./docs/fable-review-contract.md).

## License

MIT
