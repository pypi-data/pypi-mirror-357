import httpx
import os
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP
from datetime import datetime

# 从环境变量获取元数据服务URL（实际部署时需要配置）
METADATA_SERVICE_URL = os.getenv("server", "http://127.0.0.1:8000")
CONST_PROJECT = os.getenv("project", "")


# Initialize FastMCP server
mcp = FastMCP("mm_dev_mcp", "developer code API Integration")


async def make_metadata_request(
    path: str, json: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    向元数据服务发送 POST 请求，并处理响应。
    """
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    url = f"{METADATA_SERVICE_URL}/{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=json, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"请求失败: {url}，状态码: {e.response.status_code}，内容: {e.response.text}"
            ) from e
        except Exception as e:
            raise RuntimeError(f"无法访问元数据服务: {url}，错误: {str(e)}") from e


# =========mcp tool 服务定义开始===========

@mcp.tool(
    name="get_code_metadata",
    description="依据项目和代码路径（包名），获取代码对应的业务模块、业务对象、代码类型等元数据信息",
)
async def get_code_metadata(package_name: str, project:str) -> Dict[str, Any]:
    """
    依据项目和代码路径或者包名，获取代码所属的业务模块、业务对象、代码类型等元数据信息

    参数:
        package_name: 包名可路径可以是包名,也可以是代码路径,如: com.yonyou.biz.mm.plan.exception.cmp.demand
        project: 项目编码或者项目名称
    返回:
        solution_type: 解决方案类型(BE: 后端,FE: 前端)
        project_type: 项目类型(entity、repository、resource、exception、operation、service、gateway、config、bootstrap、sdk)
        project: 项目编码/名称
        compontent_type: 组件类型(entity、enum、dto、repository、resource、exception、operation、service、gateway、ref、bootstrap、util、test)
        micro_code: 微服务编码
        business_module: 所属业务模块
        business_object: 所属业务对象
        stdand_file_path: 标准文件路径
        description: 描述
    """
    if not package_name:
        raise ValueError("代码包名或者文件路径 不能为空")

    if not project:
        raise ValueError("项目不能为空")

    payload = {
        "project": project,
        "package_name": package_name,
    }
    return await make_metadata_request("solution/code/metadata", payload)


@mcp.tool(
    name="get_exception_code",
    description="获取异常编码: 依据项目、业务模块、业务对象、异常内容，获取异常编码",
)
async def get_exception_code(
    project: str, 
    business_module: str, 
    business_object: str, 
    exception_content: str
) -> Dict[str, Any]:
    """
    依据项目、业务模块、业务对象、异常内容，获取异常编码

    参数:
        project: 项目
        business_module: 业务模块
        business_object: 业务对象
        exception_content: 异常内容
    返回:
        exception_id: 异常ID
        exception_code: 异常编码
        stdand_file_path: 标准文件路径
        description: 描述
    """
    if not project:
        raise ValueError("项目 不能为空")
    if not business_module:
        raise ValueError("业务模块 不能为空")
    if not business_object:
        raise ValueError("业务对象 不能为空")
    if not exception_content:
        raise ValueError("异常内容 不能为空")

    payload = {
        "project": project,  # 使用传入的project参数而不是常量
        "business_module": business_module,
        "business_object": business_object,
        "exception_content": exception_content,
    }
    return await make_metadata_request("solution/exception/metadata", payload)


@mcp.tool(
    name="get_generate_code_prompts",
    description="在生成代码前，务必请调用此工具，获取代码生成规则、代码优化规则。",
)
def get_generate_code_prompts(topic: Optional[str] = None) -> str:
    """在生成代码前，务必请调用此工具，获取代码生成规则、代码优化规则。"""

    # 获取当前日期并格式化为字符串
    current_date = datetime.now().strftime("%Y-%m-%d")

    rule_item = f"""
    所有的类和方法都需要加上注解:@AICode(type = AICodeTypeEnum.CODE_GENERATION, author = "作者", date = "{current_date}", remark = "业务功能描述")
    AICode注解包在com.yonyou.biz.mm.common.annotation下。type=CODE_GENERATION|CODE_OPTIMIZATION|WHITE_BOX_TESTING
    """

    return rule_item


# =========mcp tool 服务定义结束===========


# =========mcp prompt 服务定义开始===========
@mcp.prompt(
    name="generate_code_request",
    description="生成代码注意事项"
)
def generate_code_request(language: str, task_description: str) -> str:
    """生成代码注意事项"""

    # 获取当前日期并格式化为字符串
    current_date = datetime.now().strftime("%Y-%m-%d")

    rule_item = f"""
    所有的类和方法都需要加上注解:@AICode(type = AICodeTypeEnum.CODE_GENERATION, author = "作者", date = "{current_date}", remark = "业务功能描述")
    AICode注解包在com.yonyou.biz.mm.common.annotation下。type=CODE_GENERATION|CODE_OPTIMIZATION|WHITE_BOX_TESTING
    """
    return rule_item


# =========mcp prompt 服务定义结束===========
def main()->None:
    # 启动 FastMCP 服务
    mcp.run(transport="stdio")
if __name__ == "__main__":
    main()