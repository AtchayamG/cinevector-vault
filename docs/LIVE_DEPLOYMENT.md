# 🚀 CineVector Vault — Live Deployment & Truthful Hybrid Execution Guide

## 1. Overview & Cloud Run Readiness

**CineVector Vault** (Track 2 — ClickHouse Partner Track) is architected for containerized deployment on **Google Cloud Run** with a **truthful hybrid execution model**. In real-world enterprise deployments, Google Gemini and ClickHouse Cloud have distinct infrastructure, security, and authentication topologies:

- **Google Gemini (Live)**: Runs securely on Google Cloud Run leveraging **Application Default Credentials (ADC)** via the Cloud Run runtime service account (Vertex AI), avoiding static API keys in production.
- **ClickHouse Cloud / MCP (Live or Demo)**: Connects to a managed ClickHouse Cloud cluster or official `mcp-clickhouse` server using dedicated database credentials, independent of Google Cloud IAM.

The system supports running in:
1. **Hybrid Mode**: Live Gemini (via Cloud Run ADC) + Demo ClickHouse (local MergeTree reference fixtures).
2. **Fully Live Mode**: Live Gemini + Live ClickHouse Cloud cluster.
3. **Deterministic Demo Mode**: Local fixtures for both providers, enabling offline demonstration and deterministic integration testing.

---

## 2. Truthful Hybrid Runtime Configuration

The runtime mode is governed by granular environment variables:

| Environment Variable | Description | Default | Valid Options |
|---|---|---|---|
| `RUNTIME_MODE` | Global runtime mode fallback | `demo` | `demo`, `live` |
| `GEMINI_RUNTIME_MODE` | Gemini 3.7 Flash extraction mode | `${RUNTIME_MODE}` | `demo`, `live` |
| `PARTNER_RUNTIME_MODE` | ClickHouse MCP & DB query mode | `${RUNTIME_MODE}` | `demo`, `live` |

### Runtime Matrix & Truthful Reporting

The top-level health endpoint (`/api/v1/health`) reports the effective top-level `runtime_mode` and independent provider evidence:

| `GEMINI_RUNTIME_MODE` | `PARTNER_RUNTIME_MODE` | Reported `runtime_mode` | Gemini Status | ClickHouse Status |
|---|---|---|---|---|
| `demo` | `demo` | `demo` | `DEMO_MODE_ACTIVE` | `DEMO_MODE_ACTIVE` |
| `live` | `demo` | `hybrid` | `LIVE_CONFIGURED`* | `DEMO_MODE_ACTIVE` |
| `demo` | `live` | `hybrid` | `DEMO_MODE_ACTIVE` | `LIVE_CONFIGURED`* |
| `live` | `live` | `live` | `LIVE_CONFIGURED`* | `LIVE_CONFIGURED`* |

*\*Note: If a provider is in `live` mode but lacks required credentials, its status reports `LIVE_UNCONFIGURED` and requests fail closed.*

---

## 3. Google Cloud Run Application Default Credentials (ADC) for Gemini

When deployed on Cloud Run, the application utilizes the native Google Cloud metadata service and instance identity.

### Required IAM Roles
The Cloud Run service account must be granted:
- **Vertex AI User** (`roles/aiplatform.user`) on the Google Cloud project.

### Configuration Variables
```bash
# Cloud Run automatically sets K_SERVICE and project metadata
GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
GOOGLE_CLOUD_LOCATION="global"
GEMINI_RUNTIME_MODE="live"
```

### Authentication Flow
1. The `google-genai` SDK initializes `genai.Client(vertexai=True, project=GOOGLE_CLOUD_PROJECT, location="global")`.
2. Cloud Run automatically signs requests using the attached service account credentials via the local metadata server (`169.254.169.254`).
3. No static API key (`GEMINI_API_KEY`) is stored or transmitted in the container.
4. For non-GCP or local development, `GEMINI_API_KEY` remains supported as an alternative authentication method.

---

## 4. ClickHouse Cloud & MCP Server Configuration

ClickHouse operates independently of Google Cloud IAM. Production credentials must be supplied explicitly, preferably via **Google Cloud Secret Manager**.

### Required Environment Variables
```bash
PARTNER_RUNTIME_MODE="live"
CLICKHOUSE_HOST="your-cluster.us-east-1.aws.clickhouse.cloud"
CLICKHOUSE_PORT=8443
CLICKHOUSE_USER="default"
CLICKHOUSE_PASSWORD="your-secure-cluster-password"
CLICKHOUSE_DATABASE="cinevector_vault"
CLICKHOUSE_SECURE="true"
```

### Secret Manager Recommendation
Map `CLICKHOUSE_PASSWORD` in Cloud Run from Google Secret Manager:
```bash
gcloud run deploy cinevector-vault \
  --set-secrets CLICKHOUSE_PASSWORD=clickhouse-vault-password:latest \
  ...
```

### Official `mcp-clickhouse` Transport
- In live mode, `ClickHouseMCPClient` connects to the installed official `mcp-clickhouse` server process via stdio using the official Python `mcp` SDK (`StdioServerParameters`, `stdio_client`, `ClientSession`).
- Live ClickHouse environment variables are securely injected into the MCP server process environment without writing secrets to disk.

---

## 5. Fail-Closed Security Guarantee

The system strictly enforces a **fail-closed** policy for all live providers:
- If `GEMINI_RUNTIME_MODE=live` and Gemini credentials are unavailable or the API call fails, the service returns `{ "success": false, "mode": "live_unavailable" | "live_error" }`. **It never silently substitutes mock tokens.**
- If `PARTNER_RUNTIME_MODE=live` and ClickHouse is unreachable, the MCP client returns `{ "status": "error", "mode": "live_unavailable" | "live_error" }`. **It never silently falls back to local fixtures.**

---

## 6. Cloud Run Container Specification & Deployment Runbook

### Container Contract
- **Base Image**: `python:3.11-slim`
- **Port Handling**: Cloud Run provides the port via the `$PORT` environment variable (default: `8080`).
- **Entrypoint**: `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}`
- **Files**:
  - `backend/Dockerfile`: Minimal production container build
  - `backend/.dockerignore`: Prevents secrets, virtual environments, caches, and test artifacts from entering the image

### Operator Deployment Steps (Reference)

```bash
# 1. Build and push container to Google Artifact Registry
gcloud builds submit backend \
  --tag gcr.io/$PROJECT_ID/cinevector-vault:latest

# 2. Deploy to Cloud Run with Hybrid Mode (ADC for Gemini, Demo or Live for ClickHouse)
gcloud run deploy cinevector-vault \
  --image gcr.io/$PROJECT_ID/cinevector-vault:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars RUNTIME_MODE=demo,GEMINI_RUNTIME_MODE=live,GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=global \
  --service-account cinevector-sa@$PROJECT_ID.iam.gserviceaccount.com

# 3. Verify Health
curl -s https://<cloud-run-url>/api/v1/health | jq .
```

---

## 7. Verification & Audit Disclaimer

> **IMPORTANT**: No production deployment, cloud resource provisioning, IAM mutation, or external credential creation occurred during this implementation session. All verification was executed locally using pytest and deterministic test fixtures in accordance with project constraints.
