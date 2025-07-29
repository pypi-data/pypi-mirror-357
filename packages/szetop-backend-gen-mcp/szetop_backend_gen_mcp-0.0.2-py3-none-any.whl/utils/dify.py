"""
Dify类 - 对接dify接口
@author yaoyanhua
@date 2025-05-13
"""
import mimetypes

import requests
import os

class Dify:
    """
    Dify类 - 封装Dify API调用功能
    @author yaoyanhua
    @date 2025-05-13
    """
    def __init__(self, api_key: str, api_base_url: str):
        """
        初始化方法
        @param api_key: Dify API密钥
        @param api_base_url: API基础URL
        @author yaoyanhua
        @date 2025-05-13
        """
        self.api_key = api_key
        self.api_base_url = api_base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def get_image_param(self, filepath: str, user: str) -> str:
        """
        上传图片并获取图片参数内容
        @param filepath: 图片文件路径
        @param user: 用户标识
        @return: API返回的图片参数内容，示例: 
        1、请求参数
        项目名称 (模糊查询, String, 可选)
        2、响应参数
        序号 (Integer)
        @author yaoyanhua
        @date 2025-05-13
        """
        # 1. 上传文件
        upload_url = f"{self.api_base_url}/files/upload"
        with open(filepath, 'rb') as f:
            file_name = os.path.basename(filepath)
            mime_type = mimetypes.guess_type(filepath)[0]
            files = {'file': (file_name, f, mime_type)}
            data = {'user': user}
            response = requests.post(
                upload_url,
                files=files,
                data=data,
                headers={"Authorization": self.headers["Authorization"]}
            )

        if response.status_code != 200 and response.status_code != 201:
            raise Exception(f"文件上传失败: {response.text}")
        
        file_id = response.json()["id"]
        print(f"文件上传成功, file_id: {file_id}")
        
        # 2. 发送消息
        message_url = f"{self.api_base_url}/chat-messages"
        payload = {
            "query": "请分析图片内容",
            "user": user,
            "inputs": {},
            "files": [{
                "type": "image",
                "transfer_method": "local_file",
                "upload_file_id": file_id
            }],
            "response_mode": "blocking"
        }
        
        response = requests.post(
            message_url,
            json=payload,
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"图片提取失败: {response.text}")
        
        return response.json()["answer"]