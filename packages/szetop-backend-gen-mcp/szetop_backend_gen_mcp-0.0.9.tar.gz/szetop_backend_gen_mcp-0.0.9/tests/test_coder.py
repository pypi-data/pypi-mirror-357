"""
测试Coder类的get_image_param方法
@author yaoyanhua
@date 2025-05-13
"""
import os
import pytest
from unittest.mock import patch, MagicMock

from backend_gen_server import Coder

import unittest

# 测试图片路径
TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "test_image.jpg")

@pytest.fixture
def mock_coder():
    """
    创建Coder测试实例
    @return: Coder实例
    @author yaoyanhua
    @date 2025-05-13
    """
    return Coder(api_key = "app-pYnTFIO9NGt7xFaa4q4Ow4Zk", api_base_url = "http://10.2.54.19/v1")

@pytest.mark.asyncio
async def test_get_image_param_success(mock_coder):
    """
    测试get_image_param方法成功场景
    @param mock_coder: Coder测试实例
    @author yaoyanhua
    @date 2025-05-13
    """
    # 模拟上传文件API响应
    upload_response = MagicMock()
    upload_response.status_code = 200
    upload_response.json.return_value = {"id": "test_file_id"}
    
    # 模拟发送消息API响应
    message_response = MagicMock()
    message_response.status_code = 200
    message_response.json.return_value = {"answer": "测试图片描述内容"}
    
    with patch("requests.post", side_effect=[upload_response, message_response]):
        result = mock_coder.get_image_param(TEST_IMAGE_PATH)
        assert result == "测试图片描述内容"

@pytest.mark.asyncio
async def test_get_image_param_upload_failure(mock_coder):
    """
    测试get_image_param方法上传文件失败场景
    @param mock_coder: Coder测试实例
    @author yaoyanhua
    @date 2025-05-13
    """
    # 模拟上传文件API失败响应
    upload_response = MagicMock()
    upload_response.status_code = 400
    upload_response.text = "上传文件失败"
    
    with patch("requests.post", return_value=upload_response):
        with pytest.raises(Exception, match="文件上传失败"):
            mock_coder.get_image_param(TEST_IMAGE_PATH)

@pytest.mark.asyncio
async def test_get_image_param_message_failure(mock_coder):
    """
    测试get_image_param方法发送消息失败场景
    @param mock_coder: Coder测试实例
    @author yaoyanhua
    @date 2025-05-13
    """
    # 模拟上传文件API响应
    upload_response = MagicMock()
    upload_response.status_code = 200
    upload_response.json.return_value = {"id": "test_file_id"}
    
    # 模拟发送消息API失败响应
    message_response = MagicMock()
    message_response.status_code = 400
    message_response.text = "发送消息失败"
    
    with patch("requests.post", side_effect=[upload_response, message_response]):
        with pytest.raises(Exception, match="消息发送失败"):
            mock_coder.get_image_param(TEST_IMAGE_PATH)


class TestJsonToMysqlDdl(unittest.TestCase):
    """
    json_to_mysql_ddl方法测试类
    @author yaoyanhua
    @date 2025-04-25
    """
    
    def test_json_to_mysql_ddl(self):
        """
        测试json_to_mysql_ddl方法
        @return: 无
        @author yaoyanhua
        @date 2025-04-25
        """
        test_json = {
          "table_info": {
            "name": "user_extend",
            "comment": "用户扩展表实体"
          },
          "column_info": [
            {
              "name": "EDUCATION",
              "type": "Integer",
              "comment": "学历 1大专 2本科 3研究生 4博士",
              "isPrimary": "false"
            },
            {
              "name": "SCHOOL_GRADUATION",
              "type": "String",
              "comment": "毕业学校",
              "isPrimary": "false"
            },
            {
              "name": "GRADUATION_DATE",
              "type": "Date",
              "comment": "毕业时间",
              "isPrimary": "false"
            },
            {
              "name": "NATION",
              "type": "String",
              "comment": "民族",
              "isPrimary": "false"
            },
            {
              "name": "MAJOR",
              "type": "String",
              "comment": "专业",
              "isPrimary": "false"
            },
            {
              "name": "SKILL",
              "type": "String",
              "comment": "技能",
              "isPrimary": "false"
            },
            {
              "name": "SPECIALITY",
              "type": "String",
              "comment": "特长",
              "isPrimary": "false"
            },
            {
              "name": "DIPLOMA",
              "type": "String",
              "comment": "毕业证书",
              "isPrimary": "false"
            },
            {
              "name": "PAPER_NUMBER",
              "type": "Integer",
              "comment": "发表论文数",
              "isPrimary": "false"
            },
            {
              "name": "IP",
              "type": "String",
              "comment": "ip",
              "isPrimary": "false"
            },
            {
              "name": "REMARK",
              "type": "String",
              "comment": "备注",
              "isPrimary": "false"
            }
          ]
        }

        result = Coder.json_to_mysql_ddl(test_json)
        print(result.strip())

@pytest.mark.asyncio
async def test_get_code_entire_prompt(mock_coder):
    """
    测试get_code_entire_prompt方法成功场景
    @param mock_coder: Coder测试实例
    @author yaoyanhua
    @date 2025-05-13
    """
    # 模拟实体数据
    # test_entities = {
    #     "table_info": {"name": "test_table", "comment": "测试表"},
    #     "column_info": [{"name": "id", "type": "Integer", "comment": "ID", "isPrimary": "true"}]
    # }

    test_entities = ["/d:/projects/ai/ai-demo-api/yitu-template/src/main/java/com/yitu/template/api/entity/GxrcProjectInfo.java",
    "d:\\projects\\ai\\ai-demo-api\\yitu-template\\src\\main\\java\\com\\yitu\\template\\api\\entity\\GxrcParkBaseInfo.java",
    "d:\\projects\\ai\\ai-demo-api\\yitu-template\\src\\main\\java\\com\\yitu\\template\\api\\entity\\GxrcAttachmentInfo.java"]

    # image_path = ["F:\\document\\公司\\AI\\研究\\代码辅助\\素材\\项目管理列表.png"]
    image_path = ["F:\\document\\公司\\AI\\研究\\代码辅助\\素材\\项目管理编辑.png"]

    # 创建Dify mock
    mock_dify = MagicMock()
    mock_dify.get_image_param.return_value = """1、请求参数
    <request_params>项目名称 (模糊查询, String, 可选)</request_params>
    2、响应参数
    <response_params>序号 (Integer)</response_params>"""

    result = mock_coder.get_code_entire_prompt(image_path, test_entities, "")
    assert "请求参数" in result
    assert "响应参数" in result
    print(f"=======>构建提示词：{result}")

@pytest.mark.asyncio
async def test_get_code_entire_prompt_success(mock_coder):
    """
    测试get_code_entire_prompt方法成功场景
    @param mock_coder: Coder测试实例
    @author yaoyanhua
    @date 2025-05-13
    """
    # 模拟实体数据
    test_entities = {
        "table_info": {"name": "test_table", "comment": "测试表"},
        "column_info": [{"name": "id", "type": "Integer", "comment": "ID", "isPrimary": "true"}]
    }
    
    # 创建Dify mock
    mock_dify = MagicMock()
    mock_dify.get_image_param.return_value = """1、请求参数
    <request_params>项目名称 (模糊查询, String, 可选)</request_params>
    2、响应参数
    <response_params>序号 (Integer)</response_params>"""

    # 模拟Dify实例
    with patch('src.backend_gen_server.services.coder.Dify', return_value=mock_dify):
        result = mock_coder.get_code_entire_prompt("\doc\项目管理列表.png", test_entities)
        assert "请求参数" in result
        assert "响应参数" in result
        assert "CREATE TABLE `test_table`" in result

@pytest.mark.asyncio
async def test_get_code_entire_prompt_failure(mock_coder):
    """
    测试get_code_entire_prompt方法失败场景
    @param mock_coder: Coder测试实例
    @author yaoyanhua
    @date 2025-05-13
    """

    # 创建Dify mock
    mock_dify = MagicMock()
    mock_dify.get_image_param.side_effect = Exception("图片提取失败")

    with patch('src.backend_gen_server.services.coder.Dify', return_value=mock_dify):
        with pytest.raises(Exception, match="图片提取失败"):
            mock_coder.get_code_entire_prompt("test.jpg", {})


if __name__ == '__main__':
    unittest.main()