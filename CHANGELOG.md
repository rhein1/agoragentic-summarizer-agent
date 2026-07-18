# Changelog

All notable changes to this example agent are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Offline request-contract and payment-safety tests plus a Python 3.10/3.13 CI matrix.
- Explicit `--execute`, `--confirm-spend`, and client-local `--idempotency-key` controls for routed execution.
- A 1280x640 branded social card and current public discovery links.

### Fixed

- Non-finite, zero, and negative execute ceilings now fail before any network request.
- Documentation distinguishes the process-local idempotency guard from unavailable router-level retry deduplication on `POST /api/execute`.
- Receipt identifiers, URLs, and settlement status are printed when the API returns them.
- Onboarding now uses the canonical `/api/quickstart` buyer path.
- Public copy now treats live match results as authoritative instead of implying a paid summarization route is currently available.
- `match_providers()` now checks the HTTP status code and raises on `>= 400`,
  so an invalid or missing API key surfaces an auth error (exit 1) instead of
  printing a false "No matching providers found." success (exit 0). This mirrors
  the guard already present in `execute_summary()`.

### Changed

- `AGORAGENTIC_BASE_URL` now uses the bare-origin convention
  (`https://agoragentic.com`); the agent appends the `/api` path segment itself.
  This makes the variable's meaning consistent with the sibling
  `agoragentic-openai-agents-example` repo and avoids a silent copy-paste config
  mismatch. `.env.example` documents that the value must not include `/api`.
