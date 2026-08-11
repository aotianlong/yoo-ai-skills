---
name: bitwarden-secrets
description: Securely retrieve passwords, API keys, access tokens, credentials, secure notes, TOTP codes, and other sensitive configuration from the user's Bitwarden vault through Bitwarden MCP. Use whenever a task needs an existing secret, the user asks to get or configure credentials, a required environment variable is missing, or credentials would otherwise be requested from the user. Supports Chinese and English requests such as “从 Bitwarden 获取密钥”, “配置 API Key”, “get the password from my vault”, and “use my saved token”.
---

# Bitwarden Secrets

Use Bitwarden MCP as the preferred source for existing sensitive information. Keep plaintext secrets out of conversation text, terminal output, diffs, logs, and version control.

## Workflow

1. Inspect the target application or configuration to determine the exact credential type, variable name, provider, endpoint, and expected format.
2. Check Bitwarden status. If the vault is locked, invoke the Bitwarden unlock tool. If interactive unlock is unavailable, explain that the user must unlock it or provide `BW_SESSION`; never ask for the master password in chat.
3. Sync when stale vault state could matter, then search items with the narrowest useful provider, service, domain, or credential name.
4. Disambiguate candidates using non-secret metadata such as item name, URI, username, type, and revision date. Prefer an exact service/purpose match over a generic login. Ask the user only when multiple plausible credentials remain and choosing incorrectly could change the result.
5. Retrieve only the required field with the narrow Bitwarden getter: `password`, `notes`, `totp`, `username`, or `uri`. Avoid fetching a whole item when a field getter suffices.
6. Validate only the format and presence in memory. Never print, quote, summarize, partially reveal, or include the secret in a user-facing message.
7. Use the secret directly for the requested operation. Do not persist it unless configuration is part of the user's request.

## Safe Configuration

- Prefer an ignored local secret file such as `.env`, a platform secret store, or a process environment variable appropriate to the project.
- Inspect existing configuration first and preserve unrelated values.
- When writing a local secret file, avoid embedding plaintext in shell arguments, command output, or a visible patch. Retrieve and write within one orchestrated tool call when possible, and suppress secret-bearing output.
- Restrict local secret-file permissions to `0600` where supported.
- Ensure secret files are ignored by version control. Never commit credentials.
- Verify configuration by checking that the expected key exists and has a plausible format or length; redact the value completely.
- Do not call third-party endpoints merely to test a credential unless that network action is necessary for the user's task.

## Reporting

Report the credential source by item name or service and state what was configured or used, without revealing the value. Mention permission and ignore-file protections when applicable.

If no matching item exists, say that Bitwarden was searched and request the missing credential or a more precise item name. Never fabricate or substitute a secret.
