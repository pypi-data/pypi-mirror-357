from mcp.server.fastmcp.server import FastMCP  # 使用工具期望的路径
from deepdiff import DeepDiff
import json


mcp = FastMCP("JsonDiffService")

# json对比工具
@mcp.tool()
def jsonDiff(expectKey: str, actualKey: str) -> dict:
    """执行json字符串对比"""
    try:
        expect_json = json.loads(expectKey)

        actual_json = json.loads(actualKey)

        # 执行对比
        differences = DeepDiff(expect_json, actual_json, ignore_order=True)

        return {
            "differences": differences,
            "is_identical": len(differences) == 0,
            "message": "对比完成"
        }
    except json.JSONDecodeError as e:
        return {
            "differences": [],
            "is_identical": False,
            "message": f"JSON解析错误：{str(e)}"
        }
    except Exception as e:
        return {
            "differences": [],
            "is_identical": False,
            "message": f"系统错误：{str(e)}"
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")