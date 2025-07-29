from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, Any
from pydantic import BaseModel

app = FastAPI(title="Mock Metadata Service")


class CodeMetadataRequest(BaseModel):
    project: str
    package_name: str


class ExceptionMetadataRequest(BaseModel):
    project: str
    business_module: str
    business_object: str
    exception_content: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/solution/code/metadata")
def get_code_metadata(request: CodeMetadataRequest) -> Dict[str, Any]:
    """
    获取代码元数据
    
    参数:
        project: 项目编码或者项目名称
        package_name: 包名可路径可以是包名,也可以是代码路径,如: com.yonyou.biz.mm.plan.exception.cmp.demand
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
    # 基于package_name推断组件类型和业务模块
    package_parts = request.package_name.split('.')
    
    # 推断组件类型
    component_type = "service"  # 默认值
    if "exception" in package_parts:
        component_type = "exception"
    elif "entity" in package_parts:
        component_type = "entity"
    elif "repository" in package_parts:
        component_type = "repository"
    elif "resource" in package_parts:
        component_type = "resource"
    elif "dto" in package_parts:
        component_type = "dto"
    
    # 推断业务模块和业务对象
    business_module = "DefaultModule"
    business_object = "DefaultObject"
    
    if len(package_parts) >= 6:  # com.yonyou.biz.mm.plan.xxx
        if len(package_parts) > 6:
            business_module = package_parts[6]  # plan等
        if len(package_parts) > 7:
            business_object = package_parts[7]  # 具体业务对象
    
    return {
        "solution_type": "BE",
        "project_type": component_type,
        "project": request.project,
        "compontent_type": component_type, 
        "micro_code": "16103",
        "business_module": business_module,
        "business_object": business_object,
        "stdand_file_path": f"src/main/java/{request.package_name.replace('.', '/')}",
        "description": f"{component_type} component for {business_module}"
    }


@app.post("/solution/exception/metadata")
def get_exception_metadata(request: ExceptionMetadataRequest) -> Dict[str, Any]:
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
    # 基于业务模块和对象生成异常编码
    module_code_map = {
        "plan": "001",
        "demand": "002", 
        "supply": "003",
        "order": "004",
        "inventory": "005"
    }
    
    module_code = module_code_map.get(request.business_module.lower(), "999")
    
    # 生成异常ID（模拟自增）
    exception_id = f"1000{module_code}{hash(request.exception_content) % 1000:03d}"
    
    # 生成异常编码
    exception_code = f"MM.{module_code}.001"
    
    # 生成标准文件路径
    std_file_path = f"src/main/java/com/yonyou/biz/mm/{request.business_module}/exception/{request.business_object}"
    
    return { 
        "exception_id": exception_id,
        "exception_code": exception_code,
        "stdand_file_path": std_file_path,
        "description": f"Exception for {request.business_module}.{request.business_object}: {request.exception_content}"
    }
