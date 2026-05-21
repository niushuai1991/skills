#!/bin/bash
# Playwright CLI wrapper - Session-based temporary container mode

IMAGE="mcr.microsoft.com/playwright/mcp"
CONTAINER_OUTPUT="/tmp/playwright-output"
SESSIONS_FILE="/tmp/playwright-sessions-$(id -u).json"
TIMEOUT=600  # 10 minutes

# Generate random session ID
generate_id() {
    head /dev/urandom | tr -dc 'a-z0-9' | head -c 8
}

# Load sessions from file
load_sessions() {
    if [ -f "$SESSIONS_FILE" ]; then
        cat "$SESSIONS_FILE"
    else
        echo '{"current": null, "sessions": {}}'
    fi
}

# Save sessions to file
save_sessions() {
    echo "$1" > "$SESSIONS_FILE"
}

# Get current timestamp
now_ts() {
    date +%s
}

# Clean expired sessions
clean_expired() {
    local data=$(load_sessions)
    local current_time=$(now_ts)
    local sessions=$(echo "$data" | jq -r '.sessions | keys[]' 2>/dev/null)
    
    for id in $sessions; do
        local last_activity=$(echo "$data" | jq -r ".sessions[\"$id\"].last_activity")
        if [ -n "$last_activity" ] && [ $((current_time - last_activity)) -gt $TIMEOUT ]; then
            local container=$(echo "$data" | jq -r ".sessions[\"$id\"].container")
            docker rm -f "$container" 2>/dev/null
            data=$(echo "$data" | jq "del(.sessions[\"$id\"])")
            if [ "$(echo "$data" | jq -r '.current')" = "$id" ]; then
                data=$(echo "$data" | jq '.current = null')
            fi
        fi
    done
    
    save_sessions "$data"
}

# Update session activity
update_activity() {
    local id="$1"
    local data=$(load_sessions)
    local current_time=$(now_ts)
    data=$(echo "$data" | jq ".sessions[\"$id\"].last_activity = $current_time")
    save_sessions "$data"
}

# Get container name for session
get_container() {
    local id="$1"
    local data=$(load_sessions)
    echo "$data" | jq -r ".sessions[\"$id\"].container // empty"
}

# Get current session
get_current() {
    local data=$(load_sessions)
    echo "$data" | jq -r '.current // empty'
}

# Session management
session_start() {
    clean_expired
    local id=$(generate_id)
    local container="playwright-$id"
    
    docker run -d --name "$container" --network host \
        --entrypoint="" ${IMAGE} sleep infinity >/dev/null
    
    local current_time=$(now_ts)
    local data=$(load_sessions)
    data=$(echo "$data" | jq ".sessions[\"$id\"] = {\"container\": \"$container\", \"created\": $current_time, \"last_activity\": $current_time}")
    data=$(echo "$data" | jq ".current = \"$id\"")
    save_sessions "$data"
    
    echo "$id"
}

session_stop() {
    local id="$1"
    if [ -z "$id" ]; then
        id=$(get_current)
    fi
    
    if [ -z "$id" ]; then
        echo "No session to stop"
        return
    fi
    
    local container=$(get_container "$id")
    if [ -n "$container" ]; then
        docker rm -f "$container" 2>/dev/null
    fi
    
    local data=$(load_sessions)
    data=$(echo "$data" | jq "del(.sessions[\"$id\"])")
    if [ "$(echo "$data" | jq -r '.current')" = "$id" ]; then
        data=$(echo "$data" | jq '.current = null')
    fi
    save_sessions "$data"
    
    echo "Session $id stopped"
}

session_list() {
    clean_expired
    local data=$(load_sessions)
    local current=$(echo "$data" | jq -r '.current // "none"')
    echo "Current session: $current"
    echo "$data" | jq -r '.sessions | to_entries[] | "\(.key): \(.value.container)"' 2>/dev/null || echo "No active sessions"
}

session_clean() {
    local data=$(load_sessions)
    local sessions=$(echo "$data" | jq -r '.sessions | keys[]' 2>/dev/null)
    
    for id in $sessions; do
        local container=$(echo "$data" | jq -r ".sessions[\"$id\"].container")
        docker rm -f "$container" 2>/dev/null
    done
    
    echo '{}' > "$SESSIONS_FILE"
    echo "All sessions cleaned"
}

# Copy file from container
copy_file() {
    local container="$1"
    local container_path="$2"
    local host_path="$3"
    
    docker cp "${container}:${container_path}" "${host_path}" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "File saved to: ${host_path}"
    fi
}

# Execute command with file output handling
handle_file_output() {
    local session_id="$1"
    local cmd="$2"
    shift 2
    local args=("$@")
    local container_file=""
    local host_file=""
    local cli_args=()
    
    local i=0
    while [ $i -lt ${#args[@]} ]; do
        local arg="${args[$i]}"
        
        if [[ "$arg" == --filename=* ]]; then
            host_file="${arg#--filename=}"
            container_file="${CONTAINER_OUTPUT}/$(basename "$host_file")"
            cli_args+=("--filename=${container_file}")
        elif [[ "$arg" == "--filename" ]]; then
            i=$((i + 1))
            host_file="${args[$i]}"
            container_file="${CONTAINER_OUTPUT}/$(basename "$host_file")"
            cli_args+=("--filename" "${container_file}")
        elif [[ "$cmd" == "state-save" ]] && [ $i -eq 0 ]; then
            host_file="$arg"
            container_file="${CONTAINER_OUTPUT}/$(basename "$arg")"
            cli_args+=("$container_file")
        else
            cli_args+=("$arg")
        fi
        i=$((i + 1))
    done
    
    local container=$(get_container "$session_id")
    docker exec "$container" npx -y @playwright/cli@latest "$cmd" "${cli_args[@]}" 2>&1
    
    if [ -n "$container_file" ] && [ -n "$host_file" ]; then
        copy_file "$container" "$container_file" "$host_file"
    fi
    
    update_activity "$session_id"
}

# Execute regular command
exec_cmd() {
    local session_id="$1"
    shift
    local container=$(get_container "$session_id")
    
    docker exec "$container" npx -y @playwright/cli@latest "$@" 2>&1
    update_activity "$session_id"
}

# Main
clean_expired

case "$1" in
    session)
        shift
        case "$1" in
            start)
                session_start
                ;;
            stop)
                shift
                session_stop "$@"
                ;;
            list)
                session_list
                ;;
            clean)
                session_clean
                ;;
            *)
                echo "Usage: $0 session {start|stop|list|clean}"
                ;;
        esac
        ;;
    -s)
        session_id="$2"
        shift 2
        container=$(get_container "$session_id")
        if [ -z "$container" ]; then
            echo "Session $session_id not found"
            exit 1
        fi
        case "$1" in
            screenshot|pdf|snapshot|state-save)
                cmd="$1"
                shift
                handle_file_output "$session_id" "$cmd" "$@"
                ;;
            *)
                exec_cmd "$session_id" "$@"
                ;;
        esac
        ;;
    --help|-h)
        echo "Playwright CLI wrapper - Session-based temporary container mode"
        echo ""
        echo "Session management:"
        echo "  $0 session start       Start new session"
        echo "  $0 session stop [id]   Stop session (default: current)"
        echo "  $0 session list        List active sessions"
        echo "  $0 session clean       Clean all sessions"
        echo ""
        echo "Commands (uses current session):"
        echo "  $0 <command> [args]    Execute playwright-cli command"
        echo "  $0 -s <id> <command>   Execute in specific session"
        ;;
    screenshot|pdf|snapshot|state-save)
        session_id=$(get_current)
        if [ -z "$session_id" ]; then
            echo "No active session. Run: $0 session start"
            exit 1
        fi
        cmd="$1"
        shift
        handle_file_output "$session_id" "$cmd" "$@"
        ;;
    *)
        session_id=$(get_current)
        if [ -z "$session_id" ]; then
            echo "No active session. Run: $0 session start"
            exit 1
        fi
        exec_cmd "$session_id" "$@"
        ;;
esac
