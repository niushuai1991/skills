# [故障事件] [简短描述]

- **日期**：YYYY-MM-DD
- **时间**：HH:MM - HH:MM (持续时间)
- **服务器/系统**：[hostname or service name]
- **严重程度**：P0/P1/P2/P3
- **影响范围**：[affected users/services]
- **处理人员**：[who was involved]

## 事件概述

[One paragraph summary of what happened]

## 时间线

| 时间 | 事件 | 操作/结果 |
|------|------|-----------|
| HH:MM | [事件发生] | [描述] |
| HH:MM | [发现/告警] | [描述] |
| HH:MM | [开始处理] | [描述] |
| HH:MM | [解决/恢复] | [描述] |

## 根本原因

### 直接原因
[What directly caused the issue]

### 根本原因
[Underlying root cause]

### 触发条件
[What triggered the event]

## 影响分析

### 服务影响
- [ ] 服务中断：[是/否，持续时间]
- [ ] 性能下降：[是/否，影响范围]
- [ ] 数据丢失：[是/否，影响数据]

### 用户影响
- [受影响用户数量]
- [用户感知的问题]

### 业务影响
- [对业务流程的影响]
- [经济损失（如有）]

## 排查过程与数据来源

### 数据收集方法

| 数据类型 | 命令/工具 | 输出位置 | 说明 |
|----------|-----------|----------|------|
| CPU/内存 | `free -h` | 终端输出 | 当前资源状态 |
| 进程信息 | `ps aux --sort=-%cpu` | 终端输出 | CPU占用排行 |
| 系统日志 | `journalctl --since ...` | 终端输出 | 内核/系统事件 |
| 历史数据 | `sar -u -f /var/log/sa/saXX` | 终端输出 | 历史CPU使用率 |

### 关键发现

**发现1**：[描述第一个关键发现]
- 数据来源：[命令或日志]
- 数据内容：[具体数据]
- 分析结论：[结论]

**发现2**：[描述第二个关键发现]
- 数据来源：[命令或日志]
- 数据内容：[具体数据]
- 分析结论：[结论]

## 解决方案

### 紧急处理
1. [Immediate actions taken]

### 长期修复
1. [Permanent fixes]

## 建议措施

### 短期（1-3天）
- [ ] [action item 1]
- [ ] [action item 2]

### 中期（1-2周）
- [ ] [action item 3]
- [ ] [action item 4]

### 长期（1-3月）
- [ ] [action item 5]

## 经验教训

### 做得好的
- [What went well]

### 需要改进的
- [What could be improved]

### 后续行动
- [Follow-up items]

## 参考资料

- [相关文档链接]
- [监控面板链接]
- [历史事件链接]
