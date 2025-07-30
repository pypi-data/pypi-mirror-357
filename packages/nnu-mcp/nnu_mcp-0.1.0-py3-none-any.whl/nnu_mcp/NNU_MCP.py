from mcp.server.fastmcp import FastMCP
import json
import requests

mcp = FastMCP("NNU_MCP")

BASE_URL = "http://223.2.21.14:5184/v1"
api_key = "dataset-nSLwqQ11z5OdiD1CKLk5efRr"


@mcp.tool()
def get_database_list(page: str = "1", limit: str = "20") -> dict:
    """
    获取知识库列表
    参数：
        page: 当前页码，非必须
        limit: 每页数量,非必须,默认20,范围1~100
    返回：
        请求响应的 JSON 数据
    """
    url = f"{BASE_URL}/datasets?page={page}&limit={limit}"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    # 检查状态码
    if response.status_code != 200:
        raise ValueError(f"API请求失败: {response.status_code}")

    # 检查响应内容是否为空
    content = response.text.strip()
    if not content:
        raise ValueError("服务器返回空内容")

    # 验证是否为合法JSON
    try:
        data = json.loads(content)
        return data
    except json.JSONDecodeError as e:
        print(f"无效JSON: {content[:100]}...")  # 打印前100个字符
        raise e


# de8a225d-afb7-4de7-aeda-8302c2324d41
@mcp.tool()
def search_konwledgebase(
    dataset_id: str,
    query: str,
    retrieval_model: object = {},
    external_retrieval_model: object = {},
) -> dict:
    """
    检索知识库
    参数：
        dataset_id: 知识库 ID
        query: 搜索关键词
        retrieval_model: 检索参数（选填，如不填，按照默认方式召回）
        external_retrieval_model: 未启用字段
    返回:
        返回结果
    """
    url = f"{BASE_URL}/datasets/{dataset_id}/retrieve"
    data = {
        "query": query,
        "retrieval_model": retrieval_model,
        "external_retrieval_model": external_retrieval_model,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    return response.json()
