# Changelog

All notable changes to this example agent are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

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
