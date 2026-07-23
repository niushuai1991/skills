# [安全事件] [简短描述]

- **日期**：YYYY-MM-DD
- **时间**：HH:MM (发现时间)
- **事件类型**：[入侵/泄露/违规/恶意软件]
- **严重程度**：Critical/High/Medium/Low
- **影响范围**：[affected systems/data]
- **响应人员**：[response team]

## 事件概述

[What security incident occurred]

## 事件详情

### 攻击向量
[How the attack entered]

### 攻击过程
[What the attacker did]

### 攻击结果
[What was compromised]

## 影响评估

### 数据影响
- [ ] 数据泄露：[是/否，数据类型和数量]
- [ ] 数据损坏：[是/否]
- [ ] 数据丢失：[是/否]

### 系统影响
- [ ] 系统入侵：[是/否]
- [ ] 权限提升：[是/否]
- [ ] 后门植入：[是/否]

### 业务影响
- [业务中断]
- [合规影响]
- [声誉影响]

## 时间线

| 时间 | 事件 | 来源 |
|------|------|------|
| HH:MM | [事件发生] | [log source] |
| HH:MM | [事件发现] | [log source] |
| HH:MM | [响应开始] | [action] |

## 排查过程与数据来源

### 数据收集

| 数据类型 | 来源 | 命令/工具 | 发现 |
|----------|------|-----------|------|
| 访问日志 | /var/log/auth.log | `grep "Failed password"` | [findings] |
| 进程信息 | /proc | `ps aux` | [findings] |
| 网络连接 | netstat | `netstat -tlnp` | [findings] |

### 取证信息

**恶意文件**：
- 文件路径：[path]
- 文件哈希：[hash]
- 文件描述：[description]

**异常进程**：
- 进程ID：[pid]
- 进程名称：[name]
- 父进程：[parent]

**网络连接**：
- 连接IP：[ip]
- 端口：[port]
- 协议：[protocol]

## 响应措施

### 紧急遏制
1. [Immediate containment actions]

### 根除
1. [Eradication actions]

### 恢复
1. [Recovery actions]

## 建议措施

### 短期
- [ ] [action 1]
- [ ] [action 2]

### 长期
- [ ] [action 3]
- [ ] [action 4]

## 经验教训

[Security lessons learned]

## 参考资料

- [相关安全公告]
- [安全策略文档]
- [历史安全事件]
