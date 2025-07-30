from mcp.server.fastmcp import FastMCP
from pydantic import Field
import httpx

mcp = FastMCP()
BASE_URL = "https://openmcp.agentspro.cn"

@mcp.tool()
async def query_deep_research(prompt: str = Field(description="深度研究的问题或主题")) -> str:
    """
    Name:
        深度研究分析
    Description:
        调用智能代理进行深度研究分析，获取详细的研究报告。
        支持学术研究、市场分析、行业调研等各类深度分析需求。
        
        AI会基于问题进行全面分析，包括：
        - 背景介绍和概念解释
        - 详细分析和数据支持  
        - 应用场景和实例
        - 发展趋势和前景展望
        
    Args:
        prompt: 需要研究分析的问题或主题
    Returns:
        详细的研究分析报告
    """
    try:
        url = BASE_URL + '/deep-research'
        
        # 构建请求数据
        request_data = {
            "prompt": prompt
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=60
            )
            response.raise_for_status()

        if response.status_code != 200:
            raise Exception(f"API请求失败: HTTP {response.status_code}")

        result = response.json()
        
        # 检查响应格式
        if result.get("success"):
            return result.get("result", "未获取到研究结果")
        else:
            error_msg = result.get("error", "未知错误")
            raise Exception(f"研究分析失败: {error_msg}")
            
    except httpx.HTTPError as e:
        raise Exception(f"HTTP请求失败: {str(e)}") from e
    except Exception as e:
        raise Exception(f"深度研究分析失败: {str(e)}") from e


def main() -> None:
    mcp.run(transport="stdio")
