# Agents Overview

This project contains concise Python samples for Autodesk Tandem Data APIs. This document explains how an AI agent (in VS Code) can assist with running, extending, and safely automating these scripts in this repository.

## Scope
- Guide agent-assisted workflows across files like authentication, client calls, and stream operations.
- Document configuration: credentials, regions, and run commands.
- Highlight safe practices for secrets and environment setup.

## Capabilities
- Code navigation and edits across the repo (Python).
- Run targeted checks or examples and suggest next actions.
- Summarize API usage from helper modules for faster development.

## Key Modules
- Authentication: [common/auth.py](common/auth.py)
- Client wrapper: [common/tandemClient.py](common/tandemClient.py)
- Constants: [common/constants.py](common/constants.py)
- Utils: [common/utils.py](common/utils.py)
- Example: list stream data: [streams/list-stream-data.py](streams/list-stream-data.py)

## Authentication
- Uses 2-legged OAuth via Autodesk Authentication v2.
- Token creation: see [common/auth.py](common/auth.py).
- Samples prefer per-script constants (e.g., `APS_CLIENT_ID`, `APS_CLIENT_SECRET`) defined near the top of each file for quick edits. Keep these as placeholders locally and do not commit secrets.
- Optional: you can still use environment variables or a non-committed `.env` file if you prefer not to edit scripts.
- Typical usage within samples:
  - Create token with required scopes (e.g., `data:read`).
  - Pass a token provider callback to `TandemClient`.

## Tandem Client
- Base URL: `https://developer.api.autodesk.com/tandem/v1` (set internally).
- Optional Region header: pass `region` when constructing `TandemClient` (e.g., `US`, `EMEA`, `AUS`).
- Methods cover facilities, models, elements, streams, documents, and history. See [common/tandemClient.py](common/tandemClient.py).

## Setup
- Prerequisites: Python 3.10+ (Windows supported).
- Install dependencies from [requirements.txt](requirements.txt).
- Ensure environment variables are set for your APS app credentials.

### Quick Start
- Install:
  - `pip install -r requirements.txt`
- Configure credentials and IDs in the script you will run:
  - Open the target script (e.g., [streams/list-stream-data.py](streams/list-stream-data.py)).
  - Replace the placeholder constants `APS_CLIENT_ID`, `APS_CLIENT_SECRET`, and any sample `FACILITY_URN` with your values.
- Optional (alternative): set environment variables instead of editing scripts:
  - Windows (PowerShell):
    - `$env:APS_CLIENT_ID = "<your_client_id>"`
    - `$env:APS_CLIENT_SECRET = "<your_client_secret>"`

## Example Workflows
- List stream data:
  - Review and update placeholders in [streams/list-stream-data.py](streams/list-stream-data.py).
  - Run with valid APS credentials and a facility where your app is a service.
- Enumerate streams, secrets, and reset operations via functions in [common/tandemClient.py](common/tandemClient.py).

## Safety & Secrets
- Never commit client secrets or access tokens.
- Prefer environment variables over hardcoding in samples.
- Validate permissions: ensure your app has access to target facilities/models.

## Troubleshooting
- Unauthorized (401/403): check token scopes and facility access.
- Not Found (404): verify `facilityId`/`modelId` values and default model linkage; see [common/utils.py](common/utils.py).
- Region mismatch: set `region` in `TandemClient` if your data is not in the default region.
- Empty results: confirm time ranges, schema attributes, and stream keys.

## Agent Tips
- Ask the agent to:
  - Extract and factor shared config from samples into a single helper while keeping script-level constants for quick edits.
  - Optionally add environment-variable reading as a fallback to constants.
  - Create small runners for repetitive tasks (e.g., stream listings).
- Keep changes minimal, focus on task-specific files.

## Notes
- This repository is a tutorial/sample set; production apps should add robust error handling, logging, configuration management, and secret handling.
