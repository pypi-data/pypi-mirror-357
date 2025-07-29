import datetime
import logging
from pathlib import Path
from typing import List

from ..trae.git_user import GIT_USERNAME

logger = logging.getLogger(__name__)
from ..utils.parse_java_entity import ParseJavaEntity, TableInfo
import re


class Prompt:
    __prompt_cache = {}

    def __init__(self, entity_paths: list[str], image_desc: str = None, business_logic: str = None) -> None:
        """
        初始化对象
        :param entity_paths: 实体类文件路径
        :param image_desc: 图片描述
        :param business_logic: 业务逻辑
        """
        # 解析实体类
        tables: List[TableInfo] = []
        for entity_path in entity_paths:
            table_info = ParseJavaEntity.extract_entity_info_by_path(entity_path)
            tables.append(table_info)
        self.tables = tables
        self.image_desc = image_desc
        self.business_logic = business_logic

    @staticmethod
    def get_describe_image_prompt() -> str:
        """
        获取解析图片提示词
        :return: 图片解析提示词
        """
        return Prompt.__get_prompt("describe_image", "describe_image_prompt.txt")

    @staticmethod
    def generate_list_api_prompt(request_params, response_fields, business_logic, title, table_ddl) -> str:
        """
        生成用于生成列表API的提示词
        :param request_params: 请求参数
        :param response_fields: 响应字段
        :param business_logic: 业务逻辑
        :param title: 页面标题
        :param table_ddl: 数据库表结构
        :return: 生成的提示词
        """
        model = {
            "request_params": request_params,
            "response_fields": response_fields,
            "business_rules": business_logic,
            "page_title": title,
            "table_structures": table_ddl,
            "author": GIT_USERNAME,
            "date": str(datetime.date.today()),
        }
        return Prompt.__get_prompt("list_api", "list_api_20250617.txt", model)

    @staticmethod
    def generate_general_api_prompt(page_type, request_params, response_fields, business_logic, title,
                                    entity_paths: list[str]) -> str:
        """
        生成用于生成API的提示词
        :param page_type: api类型
        :param request_params: 请求参数
        :param response_fields: 响应字段
        :param business_logic: 业务逻辑
        :param title: 页面标题
        :param entity_paths: 实体类文件列表
        :return: 生成的提示词
        """

        api_type = "列表"
        if page_type == "编辑":
            response_fields = "-返回主表的主键id"
            api_type = "新增编辑"
        elif page_type == "详情":
            request_params = "-主表的主键id"
            api_type = "详情"

        # out_ddl = []
        # for entity_path in entity_paths:
        #     table_info = ParseJavaEntity.extract_entity_info_by_path(entity_path)
        #     mysql_ddl = table_info.generate_mysql_ddl()
        #     out_ddl.append(mysql_ddl)

        prompt = Prompt(entity_paths)
        model = {
            "request_params": request_params,
            "response_fields": response_fields,
            "business_rules": business_logic,
            "page_title": title,
            "api_type": api_type,
            "table_structures": prompt.get_table_structures(),
            "author": GIT_USERNAME,
            "date": str(datetime.date.today()),
        }
        return Prompt.__get_prompt("add_api", "general_api_20250617.txt", model)

    @staticmethod
    def generate_code_list_prompt(entity_paths: list[str], image_desc: str, business_logic: str = None) -> str:
        """
        生成用于生成列表代码的提示词
        """
        prompt = Prompt(entity_paths, image_desc, business_logic)
        model = {
            "date": str(datetime.date.today()),
            "author": GIT_USERNAME,
            "business_logic": prompt.business_logic,
            "response_fields": prompt.get_response_fields(),
            "table_structures": prompt.get_table_structures(),
            "request_params": prompt.get_request_params(),
        }
        return Prompt.__get_prompt("list_api", "list_api_20250518.txt", model)

    @staticmethod
    def __get_prompt(key: str, prompt_file: str, model: dict = None) -> str:
        """
        获取提示词，优先从缓存中读取
        :param key: 提示词缓存的key
        :param prompt_file: 提示词文件的相对路径
        :param model: 需要替换的参数
        :return: 提示词
        """
        cache = Prompt.__prompt_cache
        if key not in cache:
            cache[key] = Prompt.__get_prompt_from_file("prompts/" + prompt_file)
        prompt_text = cache[key]
        if model:
            for key, value in model.items():
                prompt_text = prompt_text.replace(f"{{{{{key}}}}}", str(value)) if value else prompt_text
        return prompt_text

    @staticmethod
    def __get_prompt_from_file(prompt_path: str) -> str:
        """
        从文件中获取提示词
        :param prompt_path: 提示词路径
        :return: 提示词
        """
        this_dir = Path(__file__).parent.resolve()
        file_path = this_dir / prompt_path
        content = file_path.read_text(encoding="utf-8")
        return content.strip()

    def get_table_structures(self) -> str:
        """
        获取表结构描述
        :return: 表结构描述
        """
        table_structures = ""
        for table in self.tables:
            table_structures += f"""
# 表名：{table.table_name}，表说明：{table.description}
| 字段名 | 字段类型 | 数据库表字段 | 字段备注 |
| ---- | ---- | ---- | ---- |        
        """
            for field in table.fields:
                table_structures += f'|{field.field_name}|{field.field_type}|{field.db_field}|{field.description} |\n'
        return table_structures

    def get_request_params(self) -> str:
        """
        从图片描述中获取参数
        :param image_desc: 图片描述
        :return: 参数描述
        """
        # 从图片描述中提取参数块
        param_block_match = re.search(r"<参数>(.*?)</参数>", self.image_desc, re.DOTALL)
        param_list = []
        if param_block_match:
            param_lines = param_block_match.group(1).strip().splitlines()
            for line in param_lines:
                parts = [p.strip() for p in line.split("|")]
                if len(parts) == 3:
                    param_list.append({
                        "label": parts[0],
                        "widget": parts[1],
                        "required": parts[2]
                    })

        param_prompt = ''
        if len(param_list) > 0:
            param_prompt += f"""        
| 参数名 | 参数类型 | 是否必填 |
| ---- | ---- | ---- |
    """
            for item in param_list:
                param_prompt += f'|{item["label"]}|{item["widget"]}|{item["required"]}|\n'
        return param_prompt

    def get_response_fields(self) -> str:
        """
        从图片描述中获取响应字段
        :return: 字段描述
        """
        field_block_match = re.search(r"<字段>\s*\[(.*?)\]\s*</字段>", self.image_desc, re.DOTALL)
        fields = []
        if field_block_match:
            field_raw = field_block_match.group(1)
            fields = [f.strip() for f in field_raw.split(",")]

        response_fields = ''
        if len(fields) > 0:
            response_fields += str.join(', ', fields)
        return response_fields
