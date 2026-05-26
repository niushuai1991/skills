#!/usr/bin/env python3
"""
Spring Boot 2.x → 3.x Migration Scanner.
Scans a Java/Maven project for common migration issues.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

SEVERITY_CRITICAL = "CRITICAL"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"

COLOR_RED = "\033[91m"
COLOR_YELLOW = "\033[93m"
COLOR_GREEN = "\033[92m"
COLOR_CYAN = "\033[96m"
COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"

JAVAX_IMPORTS = {
    "javax.servlet": "jakarta.servlet",
    "javax.validation": "jakarta.validation",
    "javax.annotation": "jakarta.annotation",
    "javax.persistence": "jakarta.persistence",
    "javax.transaction": "jakarta.transaction",
    "javax.mail": "jakarta.mail",
    "javax.websocket": "jakarta.websocket",
    "javax.json": "jakarta.json",
    "javax.jms": "jakarta.jms",
    "javax.interceptor": "jakarta.interceptor",
    "javax.enterprise": "jakarta.enterprise",
    "javax.inject": "jakarta.inject",
    "javax.management.j2ee": "jakarta.management.j2ee",
}

DEPRECATED_APIS = [
    (r"(\w+)\.newInstance\(\)", "Class.newInstance()", "getDeclaredConstructor().newInstance()"),
    (r"new\s+org\.springframework\.security\.crypto\.password\.MessageDigestPasswordEncoder",
     "MessageDigestPasswordEncoder", "Use DelegatingPasswordEncoder or BCryptPasswordEncoder"),
    (r"WebMvcConfigurerAdapter", "WebMvcConfigurerAdapter", "Implement WebMvcConfigurer directly"),
    (r"WebSecurityConfigurerAdapter", "WebSecurityConfigurerAdapter", "Use SecurityFilterChain bean"),
    (r"org\.springframework\.boot\.web\.servlet\.filter\.OrderedRequestContextFilter",
     "OrderedRequestContextFilter", "Replaced by OrderedRequestContextFilter in web framework"),
    (r"org\.springframework\.security\.config\.annotation\.web\.configuration\.WebSecurityConfigurerAdapter",
     "WebSecurityConfigurerAdapter (full qual)", "Use SecurityFilterChain bean approach"),
    (r"@EnableGlobalMethodSecurity",
     "@EnableGlobalMethodSecurity", "Replaced by @EnableMethodSecurity"),
    (r"antMatchers\(",
     "antMatchers()", "Use requestMatchers() with MvcRequestMatcher or AntPathRequestMatcher"),
    (r"mvcMatchers\(",
     "mvcMatchers()", "Use requestMatchers()"),
    (r"authorizeRequests\(",
     "authorizeRequests()", "Use authorizeHttpRequests()"),
    (r"HttpTraceRepository",
     "HttpTraceRepository", "Renamed to HttpExchangeRepository"),
    (r"httptrace",
     "httptrace endpoint", "Renamed to httpexchanges"),
    (r"spring\.jpa\.hibernate\.use-new-id-generator-mappings",
     "use-new-id-generator-mappings", "Property removed, Hibernate no longer supports old ID generators"),
]

RENAMED_PROPERTIES = [
    ("server.max-http-header-size", "server.max-http-request-header-size"),
    ("spring.redis.", "spring.data.redis."),
    ("spring.data.cassandra.", "spring.cassandra."),
    ("management.metrics.export.prometheus", "management.prometheus.metrics.export"),
    ("management.metrics.export.influx", "management.influx.metrics.export"),
    ("management.metrics.export.datadog", "management.datadog.metrics.export"),
    ("management.metrics.export.newrelic", "management.newrelic.metrics.export"),
    ("management.metrics.export.graphite", "management.graphite.metrics.export"),
    ("spring.security.saml2.relyingparty.registration.{id}.identity-provider",
     "spring.security.saml2.relyingparty.registration.{id}.asserting-party"),
]

REMOVED_PROPERTIES = [
    "spring.jta.atomikos.properties.",
    "spring.activemq.",
    "spring.solr.",
    "spring.session.store-type",
    "spring.jta.log-dir",
    "spring.jta.transaction-manager-id",
]

OLD_DEPENDENCY_COORDS = {
    ("mysql", "mysql-connector-java"): ("com.mysql", "mysql-connector-j", "MySQL JDBC Driver 坐标变更"),
    ("org.hibernate", "hibernate-core"): ("org.hibernate.orm", "hibernate-core", "Hibernate groupId 变更"),
    ("org.hibernate", "hibernate-entitymanager"): ("org.hibernate.orm", "hibernate-core", "hibernate-entitymanager 已合并到 hibernate-core"),
    ("org.hibernate.validator", "hibernate-validator"): None,
    ("javax.servlet", "javax.servlet-api"): ("jakarta.servlet", "jakarta.servlet-api", "javax.servlet → jakarta.servlet"),
    ("javax.validation", "validation-api"): ("jakarta.validation", "jakarta.validation-api", "javax.validation → jakarta.validation"),
}

SPRING_BOOT_2X_VERSIONS = re.compile(r"<spring-boot\.version>(2\.\d+\.\d+)</spring-boot\.version>")
OLD_MAVEN_COMPILER_PLUGIN = re.compile(r"<maven-compiler-plugin\.version>([12]\.\d+\.\d+)</maven-compiler-plugin\.version>")

AUTOCONFIG_SPRING_FACTORIES = re.compile(
    r"org\.springframework\.boot\.autoconfigure\.EnableAutoConfiguration"
)


class MigrationScanner:
    def __init__(self, project_dir):
        self.project_dir = Path(project_dir).resolve()
        self.results = defaultdict(list)

    def _add(self, severity, category, file_path, line_num, message):
        self.results[severity].append({
            "category": category,
            "file": str(file_path.relative_to(self.project_dir)) if file_path else "",
            "line": line_num,
            "message": message,
        })

    def scan(self):
        print(f"\n{COLOR_BOLD}Scanning: {self.project_dir}{COLOR_RESET}\n")
        self._scan_javax_imports()
        self._scan_deprecated_apis()
        self._scan_pom_files()
        self._scan_config_properties()
        self._scan_spring_factories()
        self._scan_banner_files()
        return self._print_report()

    def _find_files(self, pattern, exclude_dirs=None):
        exclude = exclude_dirs or {"target", "node_modules", ".git", "build", ".idea", ".mvn"}
        for path in self.project_dir.rglob(pattern):
            if any(p in path.parts for p in exclude):
                continue
            yield path

    def _scan_javax_imports(self):
        for java_file in self._find_files("*.java"):
            try:
                content = java_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(content.splitlines(), 1):
                stripped = line.strip()
                if not stripped.startswith("import "):
                    continue
                for javax_pkg, jakarta_pkg in JAVAX_IMPORTS.items():
                    if javax_pkg in stripped:
                        self._add(SEVERITY_CRITICAL, "javax→jakarta", java_file, i,
                                  f"{stripped} → import {jakarta_pkg}.{stripped.split(javax_pkg + '.')[1]}")

    def _scan_deprecated_apis(self):
        for java_file in self._find_files("*.java"):
            try:
                content = java_file.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for i, line in enumerate(content.splitlines(), 1):
                for pattern, name, replacement in DEPRECATED_APIS:
                    if re.search(pattern, line.strip()):
                        self._add(SEVERITY_WARNING, "deprecated-api", java_file, i,
                                  f"{name} → {replacement}")

    def _scan_pom_files(self):
        for pom_file in list(self._find_files("pom.xml")):
            self._check_pom(pom_file)

    def _check_pom(self, pom_file):
        try:
            content = pom_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return

        m = SPRING_BOOT_2X_VERSIONS.search(content)
        if m:
            self._add(SEVERITY_CRITICAL, "spring-boot-version", pom_file, 0,
                       f"Spring Boot {m.group(1)} → need 3.x")

        m = OLD_MAVEN_COMPILER_PLUGIN.search(content)
        if m:
            self._add(SEVERITY_INFO, "maven-plugin", pom_file, 0,
                       f"maven-compiler-plugin {m.group(1)} → 3.11+")

        java_version = re.search(r"<java\.version>(\d+)</java\.version>", content)
        if java_version and int(java_version.group(1)) < 17:
            self._add(SEVERITY_CRITICAL, "java-version", pom_file, 0,
                       f"Java {java_version.group(1)} → 17+")

        try:
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            tree = ET.parse(pom_file)
            root = tree.getroot()
            for dep in root.iter("{http://maven.apache.org/POM/4.0.0}dependency"):
                gid = dep.find("{http://maven.apache.org/POM/4.0.0}groupId")
                aid = dep.find("{http://maven.apache.org/POM/4.0.0}artifactId")
                if gid is not None and aid is not None and gid.text and aid.text:
                    key = (gid.text, aid.text)
                    if key in OLD_DEPENDENCY_COORDS:
                        info = OLD_DEPENDENCY_COORDS[key]
                        if info is None:
                            self._add(SEVERITY_WARNING, "dependency", pom_file, 0,
                                       f"已移除: {key[0]}:{key[1]}")
                        else:
                            new_gid, new_aid, note = info
                            self._add(SEVERITY_WARNING, "dependency", pom_file, 0,
                                       f"{key[0]}:{key[1]} → {new_gid}:{new_aid} ({note})")
        except ET.ParseError:
            for old_key, info in OLD_DEPENDENCY_COORDS.items():
                gid, aid = old_key
                if gid in content and aid in content:
                    if info:
                        self._add(SEVERITY_WARNING, "dependency", pom_file, 0,
                                   f"{gid}:{aid} → {info[0]}:{info[1]} ({info[2]})")
                    else:
                        self._add(SEVERITY_WARNING, "dependency", pom_file, 0,
                                   f"已移除: {gid}:{aid}")

        if "springfox" in content.lower():
            self._add(SEVERITY_WARNING, "dependency", pom_file, 0,
                       "SpringFox 已停止维护，不兼容 Spring Boot 3.x → springdoc-openapi 2.x")
        if "fastjson" in content.lower() and "fastjson2" not in content.lower():
            self._add(SEVERITY_INFO, "dependency", pom_file, 0,
                       "Fastjson 1.x 安全漏洞，建议迁移到 Jackson 或 Fastjson2")

    def _scan_config_properties(self):
        for ext in ("*.yml", "*.yaml", "*.properties"):
            for config_file in self._find_files(ext, exclude_dirs={"target", "node_modules", ".git", "build", ".idea", ".mvn", ".mvn"}):
                self._check_config(config_file)

    def _check_config(self, config_file):
        try:
            content = config_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return
        lines = content.splitlines()
        is_yaml = config_file.suffix in (".yml", ".yaml")

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            key = stripped.split(":")[0].strip() if is_yaml else stripped.split("=")[0].strip()
            key = re.sub(r"\s+", "", key)

            for old_prop, new_prop in RENAMED_PROPERTIES:
                if key.startswith(old_prop):
                    self._add(SEVERITY_WARNING, "config-property", config_file, i,
                               f"{old_prop} → {new_prop}")

            for removed in REMOVED_PROPERTIES:
                if key.startswith(removed):
                    self._add(SEVERITY_WARNING, "config-property", config_file, i,
                               f"已移除属性: {removed}")

    def _scan_spring_factories(self):
        for sf in self._find_files("spring.factories"):
            try:
                content = sf.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if AUTOCONFIG_SPRING_FACTORIES.search(content):
                self._add(SEVERITY_WARNING, "spring.factories", sf, 0,
                           "EnableAutoConfiguration 注册方式已移除 → META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports")

    def _scan_banner_files(self):
        for ext in ("*.gif", "*.jpg", "*.jpeg", "*.png"):
            for banner in self._find_files(f"banner{ext.lstrip('*')}"):
                self._add(SEVERITY_INFO, "banner", banner, 0,
                           "Spring Boot 3.x 不再支持图片 banner → 使用 banner.txt")

    def _print_report(self):
        total = sum(len(v) for v in self.results.values())
        if total == 0:
            print(f"{COLOR_GREEN}✅ No migration issues found!{COLOR_RESET}\n")
            return 0

        severity_order = [SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO]
        severity_color = {
            SEVERITY_CRITICAL: COLOR_RED,
            SEVERITY_WARNING: COLOR_YELLOW,
            SEVERITY_INFO: COLOR_CYAN,
        }

        for sev in severity_order:
            items = self.results.get(sev, [])
            if not items:
                continue
            color = severity_color[sev]
            print(f"{color}{COLOR_BOLD}{sev} ({len(items)} issues){COLOR_RESET}")
            print(f"{color}{'─' * 60}{COLOR_RESET}")

            by_category = defaultdict(list)
            for item in items:
                by_category[item["category"]].append(item)

            for cat, cat_items in by_category.items():
                print(f"\n  [{cat}]")
                for item in cat_items:
                    loc = f"{item['file']}"
                    if item["line"]:
                        loc += f":{item['line']}"
                    print(f"    {loc}")
                    print(f"      → {item['message']}")
            print()

        print(f"{COLOR_BOLD}Summary:{COLOR_RESET} ", end="")
        parts = []
        for sev in severity_order:
            count = len(self.results.get(sev, []))
            if count:
                parts.append(f"{severity_color[sev]}{count} {sev}{COLOR_RESET}")
        print("  ".join(parts))
        print()

        critical_count = len(self.results.get(SEVERITY_CRITICAL, []))
        return 1 if critical_count > 0 else 0


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <project-directory>")
        sys.exit(1)
    project_dir = sys.argv[1]
    if not os.path.isdir(project_dir):
        print(f"Error: {project_dir} is not a directory")
        sys.exit(1)
    scanner = MigrationScanner(project_dir)
    exit_code = scanner.scan()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
