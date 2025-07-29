import datetime
import logging
import re
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)
from .extract_java_stack import ExtraJavaStack
from .cert_installer import CertInstaller
from .proxy_set import ProxySet
from .git_user import GIT_USERNAME
from .machine import Machine


class TraeEnv:
    def __init__(self, project_root: str):
        """
        初始化对象
        :param project_root: 项目根目录
        """
        self.project_root = Path(project_root).resolve()
        self.trae_dir = self.project_root / ".trae"
        self.rules_dir = self.trae_dir / "rules"

    @staticmethod
    def check_env(http_proxy):
        """
        检查环境
        """
        # 检查git环境
        if not GIT_USERNAME:
            raise Exception("请检查git环境，设置git用户信息")
        logger.info(f"GIT_USERNAME: {GIT_USERNAME}")
        # 安装代理证书
        CertInstaller.install()
        # 设置代理
        ProxySet.set_code_proxy(http_proxy)
        # TODO 将git用户名、机器ID、当前时间 插入数据库
        machine_id = Machine.get_machine_id()
        logger.info(f"machine_id: {machine_id}")

    @staticmethod
    def set_rules(project_root: str) -> None:
        """
        设置Trae的规则
        :param project_root: 项目根目录
        """
        trae = TraeEnv(project_root)
        trae.create_ignore()
        trae.create_rules()

    def create_ignore(self):
        """
        判断 project_root/.trae/.ignore 是否存在，如果存在则返回；
        否则读取当前目录下的 ignore 文件内容，写入 project_root/.trae/.ignore。
        :return:
        """
        ignore_target = self.trae_dir / ".ignore"
        if ignore_target.exists():
            return  # 已存在，不做操作

        # 确保 .trae 目录存在
        self.trae_dir.mkdir(parents=True, exist_ok=True)

        # 获取当前 .py 文件所在目录
        this_dir = Path(__file__).parent.resolve()

        # 拼接成完整路径
        ignore_file = this_dir / "ide_template/ignore"

        # 读取 ignore 文件（假设在当前工作目录）
        if not ignore_file.exists():
            raise FileNotFoundError("缺少 ignore 文件")

        logger.info(f"开始创建 ignore 文件：{ignore_target}")
        shutil.copy(ignore_file, ignore_target)
        logger.info(f"已创建 ignore 文件")

    def create_rules(self):
        """
        判断 project_root/.trae/rules/project_rules.md 是否存在，如果存在则返回；
        否则读取 trae/springboot3/project_rules.md 文件内容，写入目标路径。
        """
        # 根据SpringBoot版本切换项目规则
        # 获取当前 .py 文件所在目录
        this_dir = Path(__file__).parent.resolve()
        major_version = self.detect_springboot_major_version()
        if major_version == '2':
            source_rules = this_dir / "ide_template/springboot2/project_rules.md"
        elif major_version == '3':
            source_rules = this_dir / "ide_template/springboot3/project_rules.md"
        else:
            raise NotImplementedError
        if not source_rules.exists():
            raise FileNotFoundError(f"缺少源规则文件：{source_rules}")

        rules_target = self.rules_dir / "project_rules.md"
        if rules_target.exists():
            old_version = TraeEnv.extract_numeric_version(rules_target)
            new_version = TraeEnv.extract_numeric_version(source_rules)
            # 已存在最新版本，不做操作
            if old_version >= new_version:
                return

        # 确保 rules 目录存在
        self.rules_dir.mkdir(parents=True, exist_ok=True)

        # 检测Java技术栈
        extract_stack = ExtraJavaStack(self.project_root)
        model = {
            "date": str(datetime.date.today()),
            "java_stack_markdown": extract_stack.get_stack_markdown(),
        }

        content = source_rules.read_text(encoding="utf-8")
        for key, value in model.items():
            content = content.replace(f"{{{{{key}}}}}", str(value)) if value else content

        rules_target.write_text(content, encoding="utf-8")
        logger.info(f"已创建 project_rules.md 文件")

    @staticmethod
    def extract_numeric_version(file_path: Path) -> int:
        """
        从 Markdown 顶部提取纯数字版本号（如 v20250619 或 20250109）。
        不存在则返回 0。

        Args:
            file_path (Path): Markdown 文件路径

        Returns:
            int: 版本号整数（如 20250619），未找到返回 0
        """
        version_pattern = re.compile(r"<!--\s*文档版本\s*[:：]\s*v?(\d{6,})\s*-->")

        with file_path.open(encoding="utf-8") as f:
            for _ in range(10):  # 只读取前10行
                line = f.readline()
                if not line:
                    break
                match = version_pattern.search(line)
                if match:
                    return int(match.group(1))
        return 0

    def detect_springboot_major_version(self) -> str:
        """
        检测项目使用的 Spring Boot 主版本号（2 或 3）。

        Returns:
            str: "2"、"3" 或 "Unknown"
        """

        # 检查 pom.xml
        pom_file = self.project_root / "pom.xml"
        if pom_file.exists():
            content = pom_file.read_text(encoding="utf-8")

            # 1. 提取所有 property 定义（如 <spring.boot.version>）
            properties = dict(re.findall(r"<(\w[\w\.-]*)>([\d.]+[^<]*)</\1>", content))

            # 2. 优先查找名为 spring-boot.version 或 spring.boot.version 的定义
            version = properties.get("spring-boot.version") or properties.get("spring.boot.version")

            # 3. 如果没有定义版本，尝试直接查依赖版本
            if not version:
                match = re.search(
                    r"<groupId>org\.springframework\.boot</groupId>.*?<version>([\d.]+[^<]*)</version>",
                    content,
                    re.DOTALL
                )
                if match:
                    version = match.group(1)

            if version:
                major = re.match(r"(\d+)", version)
                if major:
                    return major.group(1)

        # 检查 Gradle 构建文件
        for gradle_file in ["build.gradle", "build.gradle.kts"]:
            file_path = self.project_root / gradle_file
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")

                # 匹配插件或依赖声明
                version_matches = re.findall(r"spring-boot.*[:=]['\"]([\d]+\.[\d.]+[^'\"]*)['\"]", content)
                for v in version_matches:
                    major = re.match(r"(\d+)", v)
                    if major:
                        return major.group(1)

        return "Unknown"
