# Spring Boot 2.x → 3.x Migration Checklist

Based on the official Spring Boot 3.0 Migration Guide.

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Core Changes](#2-core-changes)
3. [Jakarta EE Namespace](#3-jakarta-ee-namespace)
4. [Web Application Changes](#4-web-application-changes)
5. [Spring Security 6.0](#5-spring-security-60)
6. [Data Access Changes](#6-data-access-changes)
7. [Actuator Changes](#7-actuator-changes)
8. [Configuration Properties](#8-configuration-properties)
9. [Dependency Management](#9-dependency-management)
10. [Build Tool Changes](#10-build-tool-changes)
11. [Minor Version Notes (3.0→3.4)](#11-minor-version-notes)

---

## 1. Prerequisites

- [ ] **JDK 17+**: Spring Boot 3.0 requires Java 17 minimum. Java 8/11 no longer supported.
- [ ] **Upgrade to latest 2.7.x first** (recommended): Helps identify deprecations incrementally.
- [ ] **Review Spring Boot 2.x deprecations**: All deprecated classes/methods/properties removed in 3.0.
- [ ] **Review dependency compatibility**: Check third-party libs for Jakarta EE 9+ support.
- [ ] **Spring Security 5.8 intermediate upgrade** (if using Spring Security): Simplifies 6.0 migration.

## 2. Core Changes

- [ ] **Spring Boot version**: `2.x` → `3.x` in pom.xml/gradle.properties
- [ ] **Add `spring-boot-properties-migrator`** during migration (remove after):
  ```xml
  <dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-properties-migrator</artifactId>
    <scope>runtime</scope>
  </dependency>
  ```
- [ ] **Spring Framework 6.0**: Review [Spring Framework 6.0 upgrade guide](https://github.com/spring-projects/spring-framework/wiki/Upgrading-to-Spring-Framework-6.x).
- [ ] **Auto-configuration registration**: `spring.factories` with `EnableAutoConfiguration` key removed → use `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`.
- [ ] **Image banner removed**: `banner.gif`, `banner.jpg`, `banner.png` ignored → use `banner.txt`.
- [ ] **Logging date format**: Default changed to ISO-8601 `yyyy-MM-dd'T'HH:mm:ss.SSSXXX`. Set `logging.pattern.dateformat=yyyy-MM-dd HH:mm:ss.SSS` to restore old format.
- [ ] **@ConstructorBinding**: No longer needed at type level. Remove from `@ConfigurationProperties` classes.
- [ ] **YamlJsonParser removed**: Migrate to another `JsonParser` implementation if used.

## 3. Jakarta EE Namespace

Spring Boot 3.0 uses Jakarta EE 10 (Servlet 6.0, JPA 3.1, Validation 3.0).

- [ ] **javax.servlet → jakarta.servlet**
- [ ] **javax.validation → jakarta.validation**
- [ ] **javax.annotation → jakarta.annotation** (`@Resource`, `@PostConstruct`, `@PreDestroy`)
- [ ] **javax.persistence → jakarta.persistence** (if using JPA)
- [ ] **javax.transaction → jakarta.transaction**
- [ ] **javax.mail → jakarta.mail**
- [ ] **Maven dependency coordinates**: `javax.servlet:javax.servlet-api` → `jakarta.servlet:jakarta.servlet-api`, same for validation-api etc.
- [ ] **Ensure no transitive javax dependencies**: Check `mvn dependency:tree` for old Java EE jars.

## 4. Web Application Changes

- [ ] **Trailing slash matching disabled**: `/path/` no longer matches `@GetMapping("/path")` by default.
  - Fix: Add explicit routes or configure `PathMatchConfigurer.setUseTrailingSlashMatch(true)`.
- [ ] **`server.max-http-header-size` deprecated** → `server.max-http-request-header-size`.
- [ ] **Graceful shutdown phases updated**: `SmartLifecycle` phases changed. Custom implementations may need updating.
- [ ] **Jetty**: Does not support Servlet 6.0. Must downgrade to Servlet 5.0 if using Jetty.
- [ ] **Apache HttpClient**: `org.apache.httpcomponents:httpclient` removed from Spring Framework 6.0 → `org.apache.httpcomponents.client5:httpclient5`.

## 5. Spring Security 6.0

- [ ] **Remove `WebSecurityConfigurerAdapter`**: Use `SecurityFilterChain` `@Bean` instead.
- [ ] **`@EnableGlobalMethodSecurity`** → **`@EnableMethodSecurity`**.
- [ ] **`antMatchers()`** → **`requestMatchers()`** with `AntPathRequestMatcher` or `MvcRequestMatcher`.
- [ ] **`authorizeRequests()`** → **`authorizeHttpRequests()`**.
- [ ] **Dispatch types**: Security filter now applies to ALL dispatch types (REQUEST, FORWARD, ERROR, ASYNC, INCLUDE). Configure via `spring.security.filter.dispatcher-types` if needed.
- [ ] **SAML2 config**: `spring.security.saml2.relyingparty.registration.{id}.identity-provider` → `.asserting-party`.
- [ ] **ReactiveUserDetailsService**: No longer auto-configured with `AuthenticationManagerResolver`.

## 6. Data Access Changes

- [ ] **Hibernate 6.1**: New `org.hibernate.orm` groupId. `spring.jpa.hibernate.use-new-id-generator-mappings` removed.
- [ ] **MySQL JDBC Driver**: `mysql:mysql-connector-java` → `com.mysql:mysql-connector-j`.
- [ ] **Redis properties**: `spring.redis.*` → `spring.data.redis.*`.
- [ ] **Cassandra properties**: `spring.data.cassandra.*` → `spring.cassandra.*`.
- [ ] **Flyway**: Upgraded to 9.0+. Review migration guide.
- [ ] **Liquibase**: Upgraded to 4.17+. May have issues; override version if needed.
- [ ] **`spring.data` prefix reserved**: Properties under `spring.data` require Spring Data on classpath.

## 7. Actuator Changes

- [ ] **JMX endpoints**: Only `/health` exposed by default. Configure `management.endpoints.jmx.exposure.*` if needed.
- [ ] **`httptrace` → `httpexchanges`**: Endpoint and classes renamed. `HttpTraceRepository` → `HttpExchangeRepository`.
- [ ] **Actuator JSON**: Uses isolated `ObjectMapper`. Set `management.endpoints.jackson.isolated-object-mapper=false` to revert.
- [ ] **Endpoint sanitization**: All values masked by default. Configure `management.endpoint.env.show-values` / `management.endpoint.configprops.show-values`.
- [ ] **Metrics export properties**: `management.metrics.export.<product>` → `management.<product>.metrics.export`.
- [ ] **Micrometer 1.10**: Previous instrumentation deprecated. Use observation-based instrumentation.

## 8. Configuration Properties

See [property-changes.md](property-changes.md) for the complete list of renamed/removed properties.

Key actions:
- [ ] Run `spring-boot-properties-migrator` to detect issues automatically.
- [ ] Check YAML multi-document syntax: `spring.profiles:` → `spring.config.activate.on-profile:`.
- [ ] `spring.profiles.include` cannot be used in profile-specific documents → use profile groups.

## 9. Dependency Management

See [dependency-changes.md](dependency-changes.md) for detailed changes.

Key actions:
- [ ] **Removed**: EhCache 2, Apache ActiveMQ, Atomikos, Hazelcast 3, Apache Solr.
- [ ] **Ehcache3**: Must use `jakarta` classifier.
- [ ] **RxJava 1.x/2.x** management removed → RxJava 3.
- [ ] **JSON-B**: Apache Johnzon removed → Eclipse Yasson.

## 10. Build Tool Changes

### Maven
- [ ] `spring-boot:run` fork attribute (deprecated in 2.7) removed.
- [ ] Git Commit ID Plugin: `pl.project13.maven:git-commit-id-plugin` → `io.github.git-commit-id:git-commit-id-maven-plugin`.
- [ ] `maven-compiler-plugin` should be 3.11+ for JDK 17 support.
- [ ] Add `<parameters>true</parameters>` to compiler plugin (Spring Boot 3 needs parameter names).

### Gradle
- [ ] Property API changes: use `.get()` / `.set()` instead of direct property access.
- [ ] Build info excludes: null-setting replaced with name-based `excludes`.

## 11. Minor Version Notes

### 3.0 → 3.1
- Native image support (GraalVM) improved
- `spring.docker.compose` support added

### 3.1 → 3.2
- **Virtual threads** support (JDK 21+, opt-in via `spring.threads.virtual.enabled=true`)
- **RestClient** support (new fluent HTTP client)
- **JdbcClient** for lightweight JDBC operations
- **Observation API** improvements
- `spring-boot-starter-jetty` requires explicit Servlet 6.0 dependency

### 3.2 → 3.3
- **CDS (Class Data Sharing)** support for faster startup
- **Spring Security** `one-time-token-login` feature
- **Service Connection** support for ActiveMQ, Pulsar
- **Base64** resource loading support

### 3.3 → 3.4
- **Structured logging** support (JSON, Elasticsearch, etc.)
- **Failing startup** on circular references by default
- **Spring Security** OAuth2 client improvements
- **Docker Compose** service connection improvements
- `server.ssl.bundle` configuration for SSL certificates
