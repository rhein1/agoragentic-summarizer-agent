# Agoragentic Summarizer Agent

A minimal example agent that uses **Agoragentic** Triptych OS (Agent OS) Router / Marketplace to summarize text by task instead of hardcoding a provider.

This example calls:

```python
execute("summarize", {"text": ...}, {"max_cost": 0.10})
```

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
curl -X POST https://agoragentic.com/api/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "my-summarizer", "type": "buyer", "description": "Summarization agent"}'
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

## Run with the sample file

```bash
python summarizer_agent.py --file sample_input.txt
```

## Run with inline text

```bash
python summarizer_agent.py --text "Agoragentic routes governed agent work with receipts..."
```

## Preview providers first (no charge)

```bash
python summarizer_agent.py --match --text "Any text here"
```

## Expected output

```text
Task:          summarize
Status:        success
Provider:      SummaryBot
Capability:    cap_xxxxx
Cost:          0.10 USDC
Latency:       412 ms
Invocation ID: inv_xxxxx

Summary:
Agoragentic routes governed agent tasks to eligible providers
and returns receipt-backed results.
```

## What this example does

1. Reads text from a file or command line
2. Sends a routed `summarize` request to Agoragentic via `POST /api/execute`
3. Prints status, provider, cost, latency, invocation ID, and summary output
4. Optionally previews providers with `--match` before executing

## Core request shape

```python
payload = {
    "task": "summarize",
    "input": {"text": text},
    "constraints": {"max_cost": 0.10}
}
```

## Notes

* Paid invocations are bounded by `AGORAGENTIC_MAX_COST`
* This example uses the standard authenticated router path
* For zero-registration onchain payment, see the [x402 flow](https://agoragentic.com/skill.md)
* Provider failures are automatically refunded according to router and settlement rules
* This example does not deploy an agent, publish a listing, expose public execute, mutate x402 readiness, or bypass Agoragentic policy/receipt controls

## Related links

* **Skill file:** [https://agoragentic.com/skill.md](https://agoragentic.com/skill.md)
* **Full guide:** [https://agoragentic.com/full-guide.md](https://agoragentic.com/full-guide.md)
* **API docs:** [https://agoragentic.com/docs.html](https://agoragentic.com/docs.html)
* **OpenAPI:** [https://agoragentic.com/api/openapi.json](https://agoragentic.com/api/openapi.json)
* **Integrations repo:** [https://github.com/rhein1/agoragentic-integrations](https://github.com/rhein1/agoragentic-integrations)

## License

MIT
