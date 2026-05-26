#!/usr/bin/env bash
set -euo pipefail

JENKINS_URL="${JENKINS_URL:?JENKINS_URL environment variable is required}"
JENKINS_URL="${JENKINS_URL%/}/"
JENKINS_USER="${JENKINS_USER:-}"
JENKINS_TOKEN="${JENKINS_TOKEN:-}"

AUTH_FLAG=""
if [[ -n "$JENKINS_USER" && -n "$JENKINS_TOKEN" ]]; then
    AUTH_FLAG="-u${JENKINS_USER}:${JENKINS_TOKEN}"
fi

crumb_header=""


get_crumb() {
    if [[ -z "$crumb_header" ]]; then
        local crumb_response
        crumb_response=$(curl -sf ${AUTH_FLAG} "${JENKINS_URL}crumbIssuer/api/json" 2>/dev/null || echo "")
        if [[ -n "$crumb_response" ]]; then
            local crumb_field crumb_value
            crumb_field=$(echo "$crumb_response" | jq -r '.crumbRequestField')
            crumb_value=$(echo "$crumb_response" | jq -r '.crumb')
            crumb_header="-H${crumb_field}:${crumb_value}"
        fi
    fi
}


jenkins_get() {
    local path="${1#/}"
    curl -sf ${AUTH_FLAG} "${JENKINS_URL}${path}"
}


jenkins_post() {
    local path="${1#/}"
    get_crumb
    curl -sf ${AUTH_FLAG} ${crumb_header} -X POST "${JENKINS_URL}${path}"
}


cmd_list_jobs() {
    jenkins_get "api/json?tree=jobs[name,url,color]"
}


cmd_job_info() {
    local name="$1"
    jenkins_get "job/${name}/api/json"
}


cmd_build() {
    local name="$1"
    jenkins_post "job/${name}/build"
}


cmd_build_with_params() {
    local name="$1"
    shift
    local params=""
    for p in "$@"; do
        params="${params}&${p}"
    done
    params="${params#&}"
    jenkins_post "job/${name}/buildWithParameters?${params}"
}


cmd_status() {
    local name="$1" build="$2"
    jenkins_get "job/${name}/${build}/api/json?tree=result,building,duration,timestamp,estimatedDuration"
}


cmd_log() {
    local name="$1" build="$2"
    jenkins_get "job/${name}/${build}/consoleText"
}


cmd_stop() {
    local name="$1" build="$2"
    jenkins_post "job/${name}/${build}/stop"
}


cmd_queue() {
    jenkins_get "queue/api/json?tree=items[id,task[name],why,blocked,stuck,waitingSince]"
}


cmd_nodes() {
    jenkins_get "computer/api/json?tree=computer[displayName,offline,offlineReason,numExecutors]"
}


cmd_last_build() {
    local name="$1"
    jenkins_get "job/${name}/api/json?tree=lastBuild[number,url,result,building]"
}


cmd_wait_build() {
    local name="$1" build="$2"
    local interval="${3:-10}"
    while true; do
        local status
        status=$(jenkins_get "job/${name}/${build}/api/json?tree=building,result")
        local building
        building=$(echo "$status" | jq -r '.building')
        if [[ "$building" == "false" ]]; then
            echo "$status"
            return 0
        fi
        sleep "$interval"
    done
}


usage() {
    cat <<EOF
Usage: bash scripts/jenkins.sh <command> [args...]

Commands:
  list-jobs                          List all jobs
  job-info <name>                    Get job details
  build <name>                       Trigger a build
  build-with-params <name> <k=v>...  Trigger build with parameters
  status <name> <build>              Get build status
  log <name> <build>                 Get build console log
  stop <name> <build>                Stop a running build
  queue                              View build queue
  nodes                              List all nodes/agents
  last-build <name>                  Get last build info
  wait-build <name> <build> [interval]  Wait for build to complete

Environment:
  JENKINS_URL    (required) Jenkins base URL
  JENKINS_USER   (optional) Username for authentication
  JENKINS_TOKEN  (optional) API token for authentication
EOF
    exit 1
}


case "${1:-}" in
    list-jobs)       cmd_list_jobs ;;
    job-info)        cmd_job_info "${2:?Job name required}" ;;
    build)           cmd_build "${2:?Job name required}" ;;
    build-with-params) cmd_build_with_params "${2:?Job name required}" "${@:3}" ;;
    status)          cmd_status "${2:?Job name required}" "${3:?Build number required}" ;;
    log)             cmd_log "${2:?Job name required}" "${3:?Build number required}" ;;
    stop)            cmd_stop "${2:?Job name required}" "${3:?Build number required}" ;;
    queue)           cmd_queue ;;
    nodes)           cmd_nodes ;;
    last-build)      cmd_last_build "${2:?Job name required}" ;;
    wait-build)      cmd_wait_build "${2:?Job name required}" "${3:?Build number required}" "${4:-10}" ;;
    -h|--help|help)  usage ;;
    *)               echo "Unknown command: $1" >&2; usage ;;
esac
