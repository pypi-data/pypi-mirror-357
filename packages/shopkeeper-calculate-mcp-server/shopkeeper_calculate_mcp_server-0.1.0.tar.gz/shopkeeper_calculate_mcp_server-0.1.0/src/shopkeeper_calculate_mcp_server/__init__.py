from mcp.server.fastmcp import FastMCP
import numexpr as ne

mcp = FastMCP("shopkeeper calculate mcp server")

@mcp.tool()
def calculate(expression: str) -> str:
    """
    使用python的numexpr库来计算数学表达式
    注意：该工具不支持阶乘运算符，需要展开。比如：5! = 5*4*3*2*1
    """

    try:
        result = ne.evaluate(expression)
        return f"{result.item()}"
    except:
        return f"错误的表达式！"

def main() -> None:
    mcp.run(transport = "stdio")
