# Evidence Sources

Use these examples only after confirming the target system and authorization. Prefer user-provided logs, tickets, monitoring links, screenshots, and command output when direct access is unavailable.

## Fault or Performance Events

```bash
uptime
free -h
top -bn1 | head -20
ps aux --sort=-%cpu | head -20
ps aux --sort=-%mem | head -20
journalctl --since "YYYY-MM-DD HH:MM" --until "YYYY-MM-DD HH:MM" --no-pager
dmesg | tail -50
```

Use `sar` only when sysstat data exists on the target host:

```bash
sar -u -f /var/log/sa/saDD
sar -d -f /var/log/sa/saDD
```

## Network Events

```bash
ss -tlnp
netstat -tlnp
```

## Security Events

```bash
last -a
who
ps aux
ss -tunap
find /tmp -maxdepth 2 -type f -mtime -2 -ls
```

Do not delete, kill, quarantine, chmod, restart, install, or reconfigure anything during report writing unless the user explicitly changes the task from reporting to remediation.

## Application and Process Evidence

- Application logs: `/var/log/`, `/app/logs/`, service-specific log directories.
- Deployment evidence: release notes, CI/CD logs, package versions, change tickets.
- Monitoring evidence: dashboards, alert timelines, metric screenshots, exported graphs.
- Database evidence: slow query logs, migration logs, backup logs, replication status.
- Conversation evidence: incident chat records, operator notes, user-provided command output.
