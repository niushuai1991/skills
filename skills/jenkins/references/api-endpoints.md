# Jenkins API Endpoints

Base URL: `${JENKINS_URL}`

## Authentication

HTTP Basic Auth: `-u username:api_token`

CSRF Protection: GET `/crumbIssuer/api/json` → returns `crumbRequestField` and `crumb`; POST requests must include this header.

## Job Operations

| Operation | Method | Path | Notes |
|-----------|--------|------|-------|
| List all jobs | GET | `/api/json?tree=jobs[name,url,color]` | Use `tree` param to filter fields |
| Job details | GET | `/job/{name}/api/json` | Full job config |
| Job config XML | GET | `/job/{name}/config.xml` | Returns XML config |
| Create job | POST | `/createItem?name={name}` | Content-Type: application/xml |
| Delete job | POST | `/job/{name}/doDelete` | |
| Enable job | POST | `/job/{name}/enable` | |
| Disable job | POST | `/job/{name}/disable` | |
| Copy job | POST | `/createItem?name={new}&mode=copy&from={old}` | |

## Build Operations

| Operation | Method | Path | Notes |
|-----------|--------|------|-------|
| Trigger build | POST | `/job/{name}/build` | Queue URL in Location header |
| Build with params | POST | `/job/{name}/buildWithParameters?key=val` | Params in query string |
| Build info | GET | `/job/{name}/{build}/api/json` | |
| Build log | GET | `/job/{name}/{build}/consoleText` | Plain text |
| Stop build | POST | `/job/{name}/{build}/stop` | |
| Last build | GET | `/job/{name}/lastBuild/api/json` | |
| Build timeline | GET | `/job/{name}/{build}/wfapi/describe` | Pipeline only |

## Queue

| Operation | Method | Path |
|-----------|--------|------|
| View queue | GET | `/queue/api/json` |
| Cancel item | POST | `/queue/cancelItem?id={id}` |

## Nodes / Agents

| Operation | Method | Path |
|-----------|--------|------|
| List nodes | GET | `/computer/api/json` |
| Node details | GET | `/computer/{name}/api/json` |

## System

| Operation | Method | Path |
|-----------|--------|------|
| Crumb | GET | `/crumbIssuer/api/json` |
| System info | GET | `/systemInfo` | Requires web UI |
| Quiet down | POST | `/quietDown` |
| Cancel quiet | POST | `/cancelQuietDown` |
| Reload config | POST | `/reload` |
| Safe restart | POST | `/safeRestart` |
| Force restart | POST | `/restart` |

## Pipeline-Specific Endpoints

| Operation | Method | Path |
|-----------|--------|------|
| Pipeline stages | GET | `/job/{name}/{build}/wfapi/describe` |
| Approve input | POST | `/job/{name}/{build}/input/{id}/proceed` | Approve pending input |
| Reject input | POST | `/job/{name}/{build}/input/{id}/abort` |

## tree Parameter

Most GET endpoints support the `tree` parameter to reduce response size:

```
/api/json?tree=jobs[name,color,lastBuild[number,result]]
/job/{name}/api/json?tree=lastBuild[number,result,timestamp],builds[number,result]{0,5}
```

## Depth Parameter

`depth=N` controls nesting depth (default 0):

```
/api/json?depth=1  # Returns more nested object details
```

## Common tree Queries

```bash
# Lightweight job list
/api/json?tree=jobs[name,url,color]

# Job list with last build status
/api/json?tree=jobs[name,color,lastBuild[number,result]]

# Build summary
/job/{name}/{build}/api/json?tree=result,building,duration,timestamp,estimatedDuration,displayName

# Build changeset
/job/{name}/{build}/api/json?tree=changeSets[items[msg,author[fullName],commitId]]

# Test results
/job/{name}/{build}/testReport/api/json?tree=suites[cases[name,status,failedSince]]
```
