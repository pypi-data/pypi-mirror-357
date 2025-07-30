import json
import logging
import os
from typing import List
from dataclasses import asdict
import requests

from ..utils.parse_java_entity import ParseJavaEntity, TableInfo
from ..trae.git_user import GIT_USERNAME

logger = logging.getLogger(__name__)


class TraeApi:
    __api_base_url = 'http://localhost:8080/api/prompt/' or os.getenv("API_BASE_URL")

    __backend_code_gen_url = __api_base_url + "getBackendCodeGenPrompt"

    @staticmethod
    def get_backend_code_gen_prompt(image_path: list[str], entity_paths: list[str], business_logic):
        """
        获取后端代码生成提示词
        :param image_path: 图片路径
        :param entity_paths: 实体类路径
        :param business_logic: 业务逻辑
        :return: 提示词
        """
        # 暂时只取第一张
        image_path = image_path[0]
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"File {image_path} not found.")

        tables: List[TableInfo] = []
        for entity_path in entity_paths:
            table_info = ParseJavaEntity.extract_entity_info_by_path(entity_path)
            tables.append(table_info)

        # multipart/form-data 结构
        files = {
            'image': open(image_path, 'rb'),
            'user': GIT_USERNAME if GIT_USERNAME else "system",
            'entities': (None, json.dumps([asdict(table) for table in tables], ensure_ascii=False)),
            'logic': (None, business_logic),
        }
        response = requests.post(TraeApi.__backend_code_gen_url, files=files)
        print(response.request.headers)
        print("状态码:", response.status_code)
        print("响应内容:", response.text)
