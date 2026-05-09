---
name: playwright-cli
description: Use when running Playwright CLI commands to automate browser interactions, take screenshots, extract data, or test web applications.
---

# Playwright CLI Skill

## Installation
```bash
npm install -g playwright-cli
# Or use via npx: npx playwright-cli <command>
```

## Important Limitations

### Chrome Profile Conflict
- Playwright CLI **cannot connect** to an already-running Chrome instance
- If Chrome is running with a profile, that profile is locked and unavailable
- **Cannot** reuse existing logged-in sessions from your Chrome

## Commands

### Basic
```bash
playwright-cli open <url>
playwright-cli goto <url>
playwright-cli snapshot
playwright-cli screenshot
playwright-cli close
```

### With Specific Browser/Profile
```bash
# Start with specific profile
playwright-cli open <url> --browser=chrome --profile=/path/to/profile

# Use isolated (new in-memory profile)
playwright-cli open <url> --isolated
```

### Interactive
```bash
playwright-cli click <ref>
playwright-cli type <ref> "text"
playwright-cli fill <ref> "text"
playwright-cli press Enter
playwright-cli snapshot
```

### Screenshot
```bash
playwright-cli screenshot
playwright-cli screenshot --filename=output.png
```

## Key Difference from OpenClaw Browser Tool

OpenClaw's `browser` tool uses Chrome DevTools Protocol to **connect** to a running Chrome instance and can reuse your logged-in sessions. Playwright CLI **launches** its own browser instance and cannot attach to existing Chrome.

If you need to access a site that requires login and Chrome is already running with that session, **use OpenClaw's browser tool** instead of Playwright CLI.
