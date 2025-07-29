import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import javalang


@dataclass
class TableField:
    field_name: str
    field_type: str
    db_field: str
    is_primary_key: bool = False
    description: Optional[str] = ""


@dataclass
class TableInfo:
    table_name: str
    description: Optional[str] = "",
    fields: List[TableField] = [],

    @staticmethod
    def __map_type(java_type: str, db: str = "mysql") -> str:
        """
        简单 Java 类型到数据库类型映射。
        """
        java_type = java_type.strip()
        java_type_lower = java_type.lower()
        # 基础映射（大小写不敏感）
        base_map = {
            "string": "VARCHAR(255)",
            "int": "INT",
            "integer": "INT",
            "long": "BIGINT",
            "float": "FLOAT",
            "double": "DOUBLE" if db == "mysql" else "DOUBLE PRECISION",
            "boolean": "BOOLEAN",
            "short": "SMALLINT",
            "byte": "TINYINT" if db == "mysql" else "SMALLINT",
            "bigdecimal": "DECIMAL(20, 6)",
            "object": "TEXT",
            "date": "DATETIME" if db == "mysql" else "TIMESTAMP",
            "localdate": "DATE",
            "localdatetime": "DATETIME" if db == "mysql" else "TIMESTAMP",
            "datetime": "DATETIME" if db == "mysql" else "TIMESTAMP",
            "instant": "TIMESTAMP",
        }
        # 忽略泛型，比如 List<String>、Optional<Integer>
        java_type_clean = java_type_lower.split("<")[0]
        return base_map.get(java_type_clean, "TEXT")  # 默认 TEXT

    def generate_mysql_ddl(self) -> str:
        """
        生成mysql建表语句
        :return: 建表语句
        """
        fields = self.fields
        lines = [f"CREATE TABLE `{self.table_name}` ("]
        for field in fields:
            line = f"  `{field.db_field}` {TableInfo.__map_type(field.field_type, 'mysql')}"
            if field.is_primary_key:
                line += " PRIMARY KEY"
            if field.description:
                line += f" COMMENT '{field.description}'"
            lines.append(line + ",")
        lines[-1] = lines[-1].rstrip(",")  # 去掉最后一行逗号
        lines.append(f") COMMENT='{self.description}';")
        return "\n".join(lines)

    def generate_postgresql_ddl(self) -> str:
        """
        生成postgresql建表语句
        :return: 建表语句
        """
        table_name = self.table_name
        description = self.description
        fields = self.fields
        lines = [f'CREATE TABLE "{table_name}" (']
        for field in fields:
            line = f'  "{field.db_field}" {TableInfo.__map_type(field.field_type, "postgresql")}'
            if field.is_primary_key:
                line += " PRIMARY KEY"
            lines.append(line + ",")
        lines[-1] = lines[-1].rstrip(",")
        lines.append(");")
        if description:
            lines.append(f"COMMENT ON TABLE \"{table_name}\" IS '{description}';")
        for field in fields:
            if field.description:
                lines.append(
                    f"COMMENT ON COLUMN \"{table_name}\".\"{field.db_field}\" IS '{field.description}';")
        return "\n".join(lines)


class ParseJavaEntity:
    def __init__(self, java_code: str) -> None:
        """
        初始化对象
        :param java_code: java代码
        """
        self.java_code = java_code
        tree = javalang.parse.parse(self.java_code)
        self.clazz = next((type for type in tree.types if isinstance(type, javalang.tree.ClassDeclaration)), None)
        if not self.clazz:
            raise Exception(f"{self.java_code}")

    @staticmethod
    def __camel_to_snake(name: str) -> str:
        """驼峰转下划线"""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    @staticmethod
    def extract_entity_info_by_path(entity_path) -> TableInfo:
        """
        抽取实体信息
        :param entity_path: 实体类路径
        :return: (表信息：Dict, 字段信息：List[JavaField])
        """
        entity_path = entity_path.replace("/", "\\").lstrip("\\")
        if not Path(entity_path).exists():
            raise FileNotFoundError(f"{entity_path}")
        with open(entity_path, encoding="utf-8") as f:
            java_code = f.read()
        parse = ParseJavaEntity(java_code)
        table_info = parse.extract_table_info()
        table_info.fields = parse.extract_table_fields()
        return table_info

    def extract_class_comment(self) -> str:
        pattern = re.compile(r"/\*\*(.*?)\*/\s*(?:@.*\s*)*class\s+\w+", re.DOTALL)
        match = pattern.search(self.java_code)
        if match:
            lines = re.findall(r"\*\s*(.*?)\s*$", match.group(1), re.MULTILINE)
            return " ".join(lines).strip()
        return ""

    @staticmethod
    def __get_annotations_value(annotations: list) -> dict[str, dict[str, Optional[str]]]:
        values = {}
        for annotation in annotations:
            values[annotation.name] = ParseJavaEntity.__get_annotation_value(annotation)
        return values

    @staticmethod
    def __get_annotation_value(annotation) -> dict[str, Optional[str]] | None:
        element = annotation.element
        if element is None:
            return None
        values = {}
        if isinstance(element, list):
            for item in element:
                name = item.name
                value = item.value
                if isinstance(value, str):
                    values[name] = value.strip('"')
                elif isinstance(value, javalang.tree.Literal):
                    values[name] = value.value.strip('"')
                else:
                    values[name] = ''
        else:
            values["value"] = annotation.element.value.strip('"')
        return values

    def extract_table_info(self) -> TableInfo:
        # 表名，默认类名转小驼峰
        table_name = ParseJavaEntity.__camel_to_snake(self.clazz.name)
        annotations_value = ParseJavaEntity.__get_annotations_value(self.clazz.annotations)

        # 获取表名
        if 'TableName' in annotations_value:
            table_name = annotations_value['TableName'].get("value")

        # 获取表注释
        table_comment = ""
        if "Schema" in annotations_value:
            schema_value = annotations_value['Schema']
            table_comment = next(
                (schema_value[k] for k in ['name', 'description', 'defaultValue'] if k in schema_value), None)
        elif 'ApiModel' in annotations_value:
            table_comment = annotations_value['ApiModel'].get("value")
        return TableInfo(table_name, table_comment)

    def extract_table_fields(self) -> List[TableField]:
        result: List[TableField] = []
        for field in self.clazz.fields:
            # 字段名可能是多个变量（如：int a, b, c;）这里只取第一个
            var_decl = field.declarators[0]
            field_name = var_decl.name
            field_type = field.type.name if hasattr(field.type, 'name') else str(field.type)

            description = ""
            db_field = field_name
            is_primary_key = False

            annotations_value = ParseJavaEntity.__get_annotations_value(field.annotations)
            # 表字段
            if 'TableId' in annotations_value:
                db_field = annotations_value['TableId'].get("value")
                is_primary_key = True
            elif 'TableField' in annotations_value:
                db_field = annotations_value['TableField'].get("value")
            # 属性备注
            if 'Schema' in annotations_value:
                schema_value = annotations_value['Schema']
                description = next(
                    (schema_value[k] for k in ['name', 'description', 'defaultValue'] if k in schema_value),
                    None)
            elif 'ApiModelProperty' in annotations_value:
                description = annotations_value['ApiModelProperty'].get("value")

            result.append(TableField(
                field_name=field_name,
                field_type=field_type,
                db_field=db_field,
                description=description,
                is_primary_key=is_primary_key
            ))
        return result
