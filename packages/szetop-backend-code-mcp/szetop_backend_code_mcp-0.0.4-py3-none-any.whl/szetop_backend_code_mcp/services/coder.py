"""
Coder类 - 代码生成
@author yaoyanhua
@date 2025-05-13
"""
import logging
import re

logger = logging.getLogger(__name__)

from ..prompt.prompt import Prompt
from ..utils.dify import Dify
from ..trae.git_user import GIT_USERNAME


class Coder:
    # api_key = "app-pYnTFIO9NGt7xFaa4q4Ow4Zk", api_base_url = "http://10.2.54.19/v1"
    def __init__(self, api_key: str, api_base_url: str):
        self.api_key = api_key
        self.api_base_url = api_base_url

    def get_code_entire_prompt(self, image_path: list[str], entity_paths: list[str], business_logic: str) -> str:
        """
        获取代码生成完整提示词
        @param filepath: 图片文件路径
        @param entities: 实体信息
        @param business_logic: 业务逻辑
        @return: 完整提示词
        @author yaoyanhua
        @date 2025-05-13
        """
        # 解析图片参数
        user = GIT_USERNAME if GIT_USERNAME else "system"
        dify = Dify(api_key=self.api_key, api_base_url=self.api_base_url)
        result_params = dify.get_image_param(image_path[0], user)
        # result_params = """
        # <page_title>项目信息管理</page_title>
        # 1、请求参数
        # <request_params>
        # - 项目名称 (String, 可选)
        # - 行政区 (Integer, 可选)
        # - 项目类型 (Integer, 可选)
        # - 申请时间-开始 (Date, 可选，格式：yyyy-MM-dd)
        # - 申请时间-结束 (Date, 可选，格式：yyyy-MM-dd)
        # - 可租面积-最小值 (BigDecimal, 可选)
        # - 可租面积-最大值 (BigDecimal, 可选)
        # - 免租期-最小值 (Integer, 可选)
        # - 免租期-最大值 (Integer, 可选)
        # - 免租期后优惠租金-最小值 (BigDecimal, 可选)
        # - 免租期后优惠租金-最大值 (BigDecimal, 可选)
        # - 项目位置校准 (Integer, 可选)
        # </request_params>
        #
        # 2、响应参数
        # <response_params>
        # - 主键ID (Long)
        # - 序号 (Integer)
        # - 项目名称 (String)
        # - 行政区 (String)
        # - 项目类型 (String)
        # - 总面积 (BigDecimal)
        # - 可租 (BigDecimal)
        # - 已锁定 (BigDecimal)
        # - 已出租 (BigDecimal)
        # - 免租期 (Integer)
        # - 优惠租金 (BigDecimal)
        # - 填报日期 (Date，格式：yyyy-MM-dd)
        # - 项目位置校准 (String)
        # - 是否可查看（Boolean）
        # - 是否可编辑（Boolean）
        # - 是否可删除（Boolean）
        # </response_params>
        # """
        logger.info(f"dify api return: {result_params}")
        request_params, response_params = self.extract_params_with_regex(result_params)

        title = self.extract_title_with_regex(result_params)
        # table_ddl = self.json_to_mysql_ddl(entities)
        # parse = ParseJavaEntity(java_code)
        page_type = self.extract_page_type_with_regex(result_params)
        prompt_template = Prompt.generate_general_api_prompt(page_type, request_params, response_params, business_logic,
                                                             title, entity_paths)

        logger.info(f"prompt template: {prompt_template}")
        result = prompt_template
        return result

    def extract_page_type_with_regex(self, content: str) -> str:
        """
        从内容中提取页面类型
        @param content: 被提取信息的内容
        @return: 页面类型
        @author yaoyanhua
        @date 2025-05-13
        """
        page_type_match = re.search(r'<page_type>(.*?)</page_type>', content, re.DOTALL)
        page_type = page_type_match.group(1).strip() if page_type_match else ""

        return page_type

    def extract_title_with_regex(self, content: str) -> str:
        """
        从内容中提取标题
        @param content: 被提取信息的内容
        @return: 标题
        @author yaoyanhua
        @date 2025-05-13
        """
        title_match = re.search(r'<page_title>(.*?)</page_title>', content, re.DOTALL)
        title = title_match.group(1).strip() if title_match else ""

        return title

    def extract_params_with_regex(self, content: str) -> tuple:
        """
        从内容中提取请求参数和响应参数
        @param content: 包含参数信息的内容
        @return: 包含请求参数和响应参数的元组
        @author yaoyanhua
        @date 2025-05-13
        """
        request_match = re.search(r'<request_params>(.*?)</request_params>', content, re.DOTALL)
        request_params = request_match.group(1).strip() if request_match else ""

        # 提取响应参数
        response_match = re.search(r'<response_params>(.*?)</response_params>', content, re.DOTALL)
        response_params = response_match.group(1).strip() if response_match else ""

        return request_params, response_params
