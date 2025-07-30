"""
测试API接口
@author ligui
@date 2025-06-24
"""
import unittest

from szetop_backend_code_mcp.services.api import TraeApi

image_file = ["E:\\Code\\ai-demo-api\\doc\\项目管理列表.png"]
entities = [
    "E:\\Code\\ai-demo-api\\yitu-template\\src\\main\\java\\com\\yitu\\template\\api\\entity\\GxrcProjectInfo.java"]


def test_get_prompt():
    TraeApi.get_backend_code_gen_prompt(image_file, entities, business_logic="不要注释")


if __name__ == '__main__':
    unittest.main()
