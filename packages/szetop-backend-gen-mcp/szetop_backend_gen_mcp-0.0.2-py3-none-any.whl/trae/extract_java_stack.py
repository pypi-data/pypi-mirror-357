#!/usr/bin/env python3
# 提取 Java 项目的技术栈信息
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional


class ExtraJavaStack:
    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()

    @staticmethod
    def resolve_version(version_str: str, properties: dict) -> str:
        if not version_str:
            return ""
        # 匹配 ${...} 并替换为实际值
        match = re.fullmatch(r"\$\{(.+?)\}", version_str.strip())
        if match:
            key = match.group(1)
            return properties.get(key, version_str)
        return version_str.strip()

    @staticmethod
    def extract_properties(root, ns) -> dict:
        props = {}
        properties_elem = root.find("m:properties", ns)
        if properties_elem is not None:
            for child in properties_elem:
                tag = child.tag.split("}", 1)[-1]  # 去掉命名空间前缀
                if child.text:
                    props[tag] = child.text.strip()
        return props

    def detect_java_project_type(self) -> str:
        """
        判断项目是 Maven 还是 Gradle 工程。

        Returns:
            str: "maven" / "gradle" / "unknown"
        """
        if (self.project_root / "pom.xml").exists():
            return "maven"
        elif (self.project_root / "build.gradle").exists() or (self.project_root / "build.gradle.kts").exists():
            return "gradle"
        else:
            return "unknown"

    def parse_dependencies(self) -> dict:
        """
        解析依赖
        :return: 返回依赖
        """
        project_type = self.detect_java_project_type()
        if project_type == "maven":
            return self.__parse_pom_dependencies()
        elif project_type == "gradle":
            return self.__parse_gradle_dependencies()
        else:
            raise NotImplementedError("Unknown project type")

    def __parse_pom_dependencies(self) -> dict:
        """
        解析POM依赖
        :return: 返回依赖
        """
        result: dict[str, Optional[str]] = {
            "JDK": None,
            "Spring Boot": None,
            "MyBatis Plus": None,
            "MySQL": None,
            "Slf4j": None,
            "Logback": None,
            "Redis": None,
            "Swagger": None,
        }

        pom_path = Path(self.project_root / 'pom.xml')
        tree = ET.parse(pom_path)
        root = tree.getroot()

        # 注册命名空间前缀
        ns = {"m": "http://maven.apache.org/POM/4.0.0"}

        # 先提取 properties
        properties = ExtraJavaStack.extract_properties(root, ns)

        # JDK 版本（来自 properties）
        jdk_version = properties["maven.compiler.source"] if "maven.compiler.source" in properties else None
        if not jdk_version:
            jdk_version = properties["maven.compiler.version"] if "maven.compiler.version" in properties else None
        if not jdk_version:
            jdk_version = properties["java.version"] if "java.version" in properties else None

        if jdk_version:
            result["JDK"] = jdk_version

        # 依赖项匹配
        for dep in root.findall(".//m:dependencies/m:dependency", ns):
            group_id = dep.find("m:groupId", ns).text if dep.find("m:groupId", ns) is not None else ""
            artifact_id = dep.find("m:artifactId", ns).text if dep.find("m:artifactId", ns) is not None else ""
            version = ExtraJavaStack.resolve_version(
                dep.find("m:version", ns).text if dep.find("m:version", ns) is not None else "", properties)

            key = f"{group_id}:{artifact_id}".lower()

            if "spring-boot-dependencies" in key:
                result["Spring Boot"] = version
            elif "mybatis-plus" in key:
                result["MyBatis Plus"] = version
            elif "mysql" in key:
                result["MySQL"] = version
            elif "slf4j" in key and not result["Slf4j"]:
                result["Slf4j"] = version
            elif "logback" in key:
                result["Logback"] = version
            elif "redis" in key:
                result["Redis"] = version
            elif "swagger" in key:
                result["Swagger"] = version

        return result

    def __parse_gradle_dependencies(self) -> dict:
        """
        解析Gradle依赖
        :return: 返回依赖
        """
        build_file = Path(self.project_root / 'build.gradle')
        content = build_file.read_text(encoding="utf-8")

        def find(pattern):
            match = re.search(pattern, content, re.IGNORECASE)
            return match.group(1).strip() if match else None

        result = {
            "JDK": find(r"java\s*\(\s*version\s*=\s*JavaVersion\.VERSION_(\d+)\s*\)"),  # Kotlin DSL 示例
            "Spring Boot": find(r"['\"]org\.springframework\.boot:spring-boot-starter(?:-[\w\-]+)?:([\w\.\-]+)['\"]"),
            "MyBatis Plus": find(r"['\"]com\.baomidou:mybatis-plus.*?:([\w\.\-]+)['\"]"),
            "MySQL": find(r"['\"]mysql:mysql-connector-java:([\w\.\-]+)['\"]"),
            "Slf4j": find(r"['\"]org\.slf4j:slf4j.*?:([\w\.\-]+)['\"]"),
            "Logback": find(r"['\"]ch\.qos\.logback:logback.*?:([\w\.\-]+)['\"]"),
            "Redis": find(r"['\"]org\.springframework\.boot:spring-boot-starter-data-redis:([\w\.\-]+)['\"]"),
            "Swagger": find(r"['\"]io\.springfox:springfox-swagger2:([\w\.\-]+)['\"]"),
        }
        return result

    def get_stack_markdown(self) -> str:
        stack = self.parse_dependencies()
        lines = []
        section_no = 1

        if stack.get("JDK"):
            lines.append(f"{section_no}. 运行环境")
            lines.append(f"   JDK {stack['JDK']}")
            section_no += 1

        if stack.get("Spring Boot"):
            lines.append(f"{section_no}. 框架依赖")
            lines.append(f"   Spring Boot {stack['Spring Boot']}")
            section_no += 1

        if stack.get("MySQL"):
            lines.append(f"{section_no}. 数据库")
            lines.append(f"   MySQL {stack['MySQL']}")
            section_no += 1

        if stack.get("MyBatis Plus"):
            lines.append(f"{section_no}. 持久层")
            lines.append(f"   MyBatis Plus {stack['MyBatis Plus']}")
            section_no += 1

        if stack.get("Slf4j") or stack.get("Logback"):
            lines.append(f"{section_no}. 日志")
            if stack.get("Slf4j"):
                lines.append(f"   Slf4j {stack['Slf4j']}")
            if stack.get("Logback"):
                lines.append(f"   Logback {stack['Logback']}")
            section_no += 1

        if stack.get("Redis"):
            lines.append(f"{section_no}. 缓存")
            lines.append(f"   Redis {stack['Redis']}")
            section_no += 1

        if stack.get("Swagger"):
            lines.append(f"{section_no}. 文档")
            lines.append(f"   Swagger {stack['Swagger']}")
            section_no += 1

        return "\n".join(lines)

# if __name__ == "__main__":
#     extract_stack = ExtraJavaStack("E:\\Code\\ai-demo-api")
#     # extract_stack = ExtraJavaStack("E:\\Code\\szetop\\ai-shopping-guide")
#     print(extract_stack.get_stack_markdown())
