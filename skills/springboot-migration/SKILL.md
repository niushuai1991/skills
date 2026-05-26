---
name: springboot-migration
description: >
  Spring Boot 2.x 到 3.x 迁移指南和自动化检查工具。支持两种模式：
  (1) migrate - 引导完整的 Spring Boot 2.x → 3.x 迁移流程（JDK 17、javax→jakarta、依赖升级、
  配置属性变更、Spring Security 6.0、废弃 API 修复等）；
  (2) check - 运行自动化扫描脚本检测迁移遗漏项（残留 javax import、废弃 API、过时依赖坐标、
  已移除配置属性等），并对照官方检查清单逐项核对。
  当用户需要升级 Spring Boot 版本、从 Spring Boot 2.x 迁移到 3.x、进行 JDK 17+ 升级、
  检查迁移完整性、评估迁移遗漏、或询问 Spring Boot 3.x 兼容性问题时使用。
---

# Spring Boot Migration

## Modes

This skill operates in two modes:

1. **`migrate`** — Guide a full Spring Boot 2.x → 3.x migration
2. **`check`** — Scan a project and audit migration completeness

Determine the mode from the user's request:
- "升级到 Spring Boot 3" / "migrate to Spring Boot 3" / "迁移" → **migrate**
- "检查迁移是否完整" / "check migration" / "scan for issues" → **check**
- Ambiguous → ask the user

---

## Mode: `check` — Migration Audit

### Step 1: Run Scanner

Run the automated scan script against the project:

```bash
python3 <skill-dir>/scripts/scan_migration.py <project-root>
```

The script detects:
- **CRITICAL**: javax imports, Spring Boot 2.x version, Java < 17
- **WARNING**: Deprecated APIs, old dependency coordinates, renamed config properties
- **INFO**: Image banners, Fastjson, SpringFox

### Step 2: Interpret Results

For each CRITICAL/WARNING issue found:
- Read the relevant file and line
- Confirm if it's a true issue or already handled
- Load [references/checklist.md](references/checklist.md) to verify against the official migration guide

### Step 3: Load Checklist for Manual Review

Read [references/checklist.md](references/checklist.md) and go through items the scanner cannot detect:
- Trailing slash matching behavior change
- `spring-boot-properties-migrator` usage
- Spring Security 6.0 patterns (`antMatchers` → `requestMatchers`, `WebSecurityConfigurerAdapter` removal)
- Dispatch types for security filter
- `@ConstructorBinding` changes
- Auto-configuration registration (`spring.factories` → `AutoConfiguration.imports`)

### Step 4: Check Property and Dependency Changes

If the project has config files or POM issues:
- Read [references/property-changes.md](references/property-changes.md) for renamed/removed properties
- Read [references/dependency-changes.md](references/dependency-changes.md) for coordinate changes and version requirements

### Step 5: Report

Generate a structured report with:
- Scanner output summary
- Manual review findings
- Prioritized action items (CRITICAL → WARNING → INFO)
- Specific file:line references

---

## Mode: `migrate` — Full Migration

### Phase Overview

| Phase | Content | Key Reference |
|---|---|---|
| 0 | Prerequisites | [checklist.md §1](references/checklist.md) |
| 1 | JDK 17 + Maven | [dependency-changes.md](references/dependency-changes.md) |
| 2 | Spring Boot 3.x + Dependencies | [dependency-changes.md](references/dependency-changes.md) |
| 3 | javax → jakarta | [checklist.md §3](references/checklist.md) |
| 4 | Configuration Properties | [property-changes.md](references/property-changes.md) |
| 5 | Web & Security | [checklist.md §4-5](references/checklist.md) |
| 6 | Data Access | [checklist.md §6](references/checklist.md) |
| 7 | Deprecated API Fixes | Scanner + manual review |
| 8 | Verify | Run scanner + `mvn clean compile` |

### Phase 0: Prerequisites

1. Create a backup branch: `git branch backup/pre-migration`
2. Verify JDK 17+ installed: `java -version`
3. Add `spring-boot-properties-migrator` dependency (remove after migration)
4. Load [references/checklist.md §1](references/checklist.md) for full prerequisite checklist

### Phase 1: JDK + Build Tool

1. Update `pom.xml`: `<java.version>17</java.version>`
2. Update `maven-compiler-plugin` to 3.11+ with `<parameters>true</parameters>`
3. See [references/dependency-changes.md](references/dependency-changes.md) for build tool changes
4. `mvn clean compile` to verify

### Phase 2: Spring Boot + Dependencies

1. Update `<spring-boot.version>` to 3.x
2. Remove version overrides managed by Spring Boot BOM (spring-framework, tomcat, logback)
3. Upgrade incompatible dependencies — load [references/dependency-changes.md](references/dependency-changes.md) for:
   - POI 4.x → 5.2+ (JDK 17 module system)
   - PageHelper 1.x → 2.x (javax.servlet dependency)
   - SpringFox → springdoc-openapi 2.x
   - Fastjson → Jackson
   - MySQL driver coordinate change
   - Hibernate groupId change
4. `mvn clean compile` — expect javax errors (fixed in Phase 3)

### Phase 3: javax → jakarta

Batch replace all `javax` imports:
- `javax.servlet` → `jakarta.servlet`
- `javax.validation` → `jakarta.validation`
- `javax.annotation` → `jakarta.annotation`
- `javax.persistence` → `jakarta.persistence`
- Also update Maven coordinates (javax.servlet:javax.servlet-api → jakarta.servlet:jakarta.servlet-api)

Run the scanner to verify zero remaining javax imports.

### Phase 4: Configuration Properties

1. Load [references/property-changes.md](references/property-changes.md)
2. Check for renamed/removed properties in all `application*.yml` and `application*.properties`
3. Check YAML multi-document syntax: `spring.profiles:` → `spring.config.activate.on-profile:`
4. Verify `spring-boot-properties-migrator` output at startup

### Phase 5: Web & Security

Load [references/checklist.md §4-5](references/checklist.md):
1. Trailing slash matching — add `PathMatchConfigurer` if needed
2. `server.max-http-header-size` → `server.max-http-request-header-size`
3. Spring Security 6.0:
   - `WebSecurityConfigurerAdapter` → `SecurityFilterChain` bean
   - `@EnableGlobalMethodSecurity` → `@EnableMethodSecurity`
   - `antMatchers()` → `requestMatchers()`
   - `authorizeRequests()` → `authorizeHttpRequests()`
4. Dispatch types — configure `spring.security.filter.dispatcher-types` if needed

### Phase 6: Data Access

Load [references/checklist.md §6](references/checklist.md):
1. Hibernate 6.1 — new groupId `org.hibernate.orm`
2. MySQL driver — new coordinates `com.mysql:mysql-connector-j`
3. Redis — `spring.redis.*` → `spring.data.redis.*`
4. Flyway 9.0+ / Liquibase 4.17+ compatibility

### Phase 7: Deprecated API Fixes

1. Run scanner to find deprecated API usage
2. Common fixes:
   - `Class.newInstance()` → `getDeclaredConstructor().newInstance()`
   - `WebMvcConfigurerAdapter` → `WebMvcConfigurer` interface
   - `WebSecurityConfigurerAdapter` → `SecurityFilterChain` bean

### Phase 8: Verify

1. Run scanner: `python3 <skill-dir>/scripts/scan_migration.py <project-root>`
2. `mvn clean compile` — zero errors
3. `mvn test` — all tests pass
4. Start application and verify functionality
5. Remove `spring-boot-properties-migrator` dependency

---

## Reference Files

| File | When to Load |
|---|---|
| [references/checklist.md](references/checklist.md) | Always in `check` mode; as needed per phase in `migrate` mode |
| [references/property-changes.md](references/property-changes.md) | When auditing/migrating config files |
| [references/dependency-changes.md](references/dependency-changes.md) | When auditing/migrating POM dependencies |
| [scripts/scan_migration.py](scripts/scan_migration.py) | First step in both modes |
