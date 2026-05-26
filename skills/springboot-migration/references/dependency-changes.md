# Dependency Changes (Spring Boot 2.x → 3.0)

## Maven Coordinate Changes

| Old Coordinates | New Coordinates | Notes |
|---|---|---|
| `mysql:mysql-connector-java` | `com.mysql:mysql-connector-j` | MySQL JDBC driver moved |
| `org.hibernate:hibernate-core` (5.x) | `org.hibernate.orm:hibernate-core` (6.1+) | Hibernate groupId changed |
| `org.hibernate:hibernate-entitymanager` | `org.hibernate.orm:hibernate-core` | Merged into hibernate-core |
| `javax.servlet:javax.servlet-api` | `jakarta.servlet:jakarta.servlet-api` | Jakarta EE namespace |
| `javax.validation:validation-api` | `jakarta.validation:jakarta.validation-api` | Jakarta EE namespace |
| `pl.project13.maven:git-commit-id-plugin` | `io.github.git-commit-id:git-commit-id-maven-plugin` | Git Commit ID plugin v5 |
| `org.apache.httpcomponents:httpclient` | `org.apache.httpcomponents.client5:httpclient5` | Apache HttpClient 5 (Spring Framework 6) |
| `io.springfox:springfox-*` | `org.springdoc:springdoc-openapi-starter-webmvc-ui` | SpringFox → springdoc-openapi |

## Minimum Version Requirements

| Dependency | Min Version for Spring Boot 3.0 |
|---|---|
| Hibernate | 6.1+ |
| Flyway | 9.0+ |
| Liquibase | 4.17+ |
| Thymeleaf | 3.1+ (managed by Spring Boot BOM) |
| Spring Security | 6.0+ (managed by Spring Boot BOM) |
| Micrometer | 1.10+ (managed by Spring Boot BOM) |
| Jackson | 2.14+ (managed by Spring Boot BOM) |
| Tomcat | 10.1+ (managed by Spring Boot BOM) |
| Logback | 1.4+ (managed by Spring Boot BOM) |

## Removed Dependencies

| Dependency | Alternative |
|---|---|
| **EhCache 2** (`net.sf.ehcache:ehcache`) | Caffeine or EhCache 3 with `jakarta` classifier |
| **Apache ActiveMQ** | Use `spring-boot-starter-artemis` or external broker |
| **Atomikos** (`com.atomikos:transactions-*`) | Use Narayana or manage transactions manually |
| **Hazelcast 3** | Upgrade to Hazelcast 5+ |
| **Apache Solr** (`spring-boot-starter-data-solr`) | No replacement (Jetty 11 incompatibility) |
| **SpringFox** (`io.springfox:*`) | `springdoc-openapi` 2.x |

## Dependency Changes Requiring Attention

| Dependency | Change |
|---|---|
| **Ehcache3** | Must use `jakarta` classifier: `org.ehcache:ehcache:jakarta` |
| **RxJava 1.x/2.x** | Dependency management removed. RxJava 3 managed instead |
| **JSON-B (Apache Johnzon)** | Dependency management removed. Use Eclipse Yasson or specify version |
| **ANTLR 2** (`antlr:antlr`) | Dependency management removed. Specify version if needed |
| **Hazelcast Hibernate** | Dependency management removed. Use `org.hibernate.orm:hibernate-jcache` |

## Common Third-Party Migration Patterns

| Library | Migration Path |
|---|---|
| **Shiro** | Not compatible with Jakarta EE. Migrate to Spring Security 6.x |
| **Fastjson 1.x** | Security vulnerabilities. Migrate to Jackson (Spring Boot built-in) or Fastjson2 |
| **POI 4.x** | Fails on JDK 17 module system. Upgrade to POI 5.2+ |
| **PageHelper 1.x** | Depends on javax.servlet. Upgrade to 2.x |
| **Kaptcha (old)** | Use `pro.fessional:kaptcha:2.3.3` (Jakarta compatible) or `kaptcha-jakarta` |
| **Druid < 1.2.23** | Upgrade to 1.2.24+ for JDK 17 support |

## Maven Compiler Plugin

For JDK 17 + Spring Boot 3, ensure:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-compiler-plugin</artifactId>
    <version>3.11.0</version>
    <configuration>
        <source>17</source>
        <target>17</target>
        <parameters>true</parameters>
    </configuration>
</plugin>
```

`<parameters>true</parameters>` is required because Spring Boot 3 relies on parameter name retention for `@PathVariable`, `@RequestParam`, etc.
