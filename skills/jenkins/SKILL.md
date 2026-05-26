---
name: jenkins
description: Jenkins CLI skill for managing jobs, builds, and nodes via REST API. Use when users need to list Jenkins jobs, trigger or stop builds, check build status or logs, view build queue, manage nodes, or perform any Jenkins operation. Also use when users mention CI/CD, continuous integration, or Jenkins-related tasks.
---

# Jenkins CLI

Manage jobs, builds, and nodes via Jenkins REST API.

## Prerequisites

- **`JENKINS_URL`** must be set (e.g. `https://jenkins.nas567.dpdns.org/`)
- **`JENKINS_USER`** and **`JENKINS_TOKEN`** for authentication (username + API Token)
- Scripts read config from environment variables; no extra config files needed

## Quick Start

```bash
# List all jobs
bash scripts/jenkins.sh list-jobs

# Trigger a build
bash scripts/jenkins.sh build <job-name>

# View build log
bash scripts/jenkins.sh log <job-name> <build-number>

# Check build status
bash scripts/jenkins.sh status <job-name> <build-number>
```

## All Commands

| Command | Script Args | Description |
|---------|-------------|-------------|
| List Jobs | `list-jobs` | Returns all job names and URLs |
| Job Info | `job-info <name>` | Returns detailed config for a single job |
| Trigger Build | `build <name>` | Triggers a parameterless build |
| Build with Params | `build-with-params <name> <key=val ...>` | Triggers a build with parameters |
| Build Status | `status <name> <build>` | Returns build result (SUCCESS/FAILURE etc.) |
| Build Log | `log <name> <build>` | Fetches console output |
| Stop Build | `stop <name> <build>` | Aborts a running build |
| Build Queue | `queue` | Lists queued builds |
| Node List | `nodes` | Lists all nodes/agents status |
| Last Build | `last-build <name>` | Gets the most recent build number and status |
| Wait for Build | `wait-build <name> <build>` | Polls until build completes and returns result |

## Authentication

Scripts use HTTP Basic Auth. Set environment variables:

```bash
export JENKINS_URL="https://jenkins.nas567.dpdns.org/"
export JENKINS_USER="your-username"
export JENKINS_TOKEN="your-api-token"
```

Generate API Token in Jenkins user settings: `User` → `Configure` → `API Token`.

## Common Workflows

### Trigger a build and wait for result

```bash
BUILD_NUM=$(bash scripts/jenkins.sh build my-job | grep -o '[0-9]*')
bash scripts/jenkins.sh wait-build my-job "$BUILD_NUM"
```

### View log of a failed build

```bash
LAST=$(bash scripts/jenkins.sh last-build my-job | jq '.number')
bash scripts/jenkins.sh log my-job "$LAST"
```

### Check queued builds

```bash
bash scripts/jenkins.sh queue
```

## Troubleshooting

**403 Forbidden**: Check that `JENKINS_USER` and `JENKINS_TOKEN` are correct.

**CSRF error (No valid crumb)**: The script auto-fetches crumb; ensure `JENKINS_URL` is reachable.

**Connection timeout**: Confirm `JENKINS_URL` ends with `/` and the network is reachable.

## References

See [references/api-endpoints.md](references/api-endpoints.md) for the full API endpoint list.
