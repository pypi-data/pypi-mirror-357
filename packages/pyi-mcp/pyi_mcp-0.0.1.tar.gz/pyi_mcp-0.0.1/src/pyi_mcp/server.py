from mcp.server.fastmcp import FastMCP
import time, random, string;
import requests
import json
from typing import Optional
import os

mcp = FastMCP(
    "PYI_MCP",
    description="Python代码解释器MCP，可以执行传入的Python代码，返回控制台输出结果。"
)

# 读取环境变量
URL = os.getenv("URL")
ID = (str(int(time.time() * 1000)) + ''.join(random.choices(string.ascii_letters + string.digits, k=10 - len(str(int(time.time() * 1000))))))[:10]
APPID = ID
UID = ID

@mcp.tool()
def python_exec(
    code_content: str,
    time_out_sec: int = 10
) -> str:
    """
    执行Python代码，并返回控制台输出。
    
    使用说明：
    1. 送入字符串形式的Python代码，获取控制台输出结果。
    
    参数：
    - code_content: 字符串形式的Python代码
    - time_out_sec: 代码执行超时限制（秒）
    
    返回：
    控制台输出的字符串内容
    """

    params = {
        "appid": APPID,
        "uid": UID
    }

    headers = {
        'Content-Type': 'application/json'
    }

    data = {
        "code": code_content,
        "timeout_sec": time_out_sec
    }

    response = requests.post(URL, params=params, headers=headers, json=data)
    
    if response.status_code != 200:
        raise Exception(response.text)

    response_json = json.loads(response.text)
    if response_json["code"] != 0:
        error_message = f"Error: {response_json['message']}"
        if response_json["data"]["stderr"]:
            error_message += f" (stderr: {response_json['data']['stderr']})"
        raise Exception(error_message)
    
    return response_json["data"]["stdout"]

def main():
    mcp.run()

if __name__ == "__main__":
    main()