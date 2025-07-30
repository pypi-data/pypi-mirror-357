import re
import json


class CurlConverter:
    """cURL命令转换工具"""

    @staticmethod
    def curl_to_python(curl_command: str) -> str:
        """将cURL命令转换为Python代码"""
        # 解析cURL命令
        method = 'GET'
        url = None
        headers = {}
        data = None

        # 移除多余空格
        curl_command = re.sub(r'\s+', ' ', curl_command).strip()

        # 提取URL
        url_match = re.search(r"curl\s+['\"]?([^'\"]+)['\"]?", curl_command)
        if url_match:
            url = url_match.group(1)

        # 提取方法
        if '-X' in curl_command:
            method_match = re.search(r'-X\s+(\w+)', curl_command)
            if method_match:
                method = method_match.group(1).upper()

        # 提取headers
        header_matches = re.finditer(r"-H\s+['\"]([^'\"]+)['\"]", curl_command)
        for match in header_matches:
            header = match.group(1)
            if ': ' in header:
                key, value = header.split(': ', 1)
                headers[key] = value

        # 提取数据
        data_match = re.search(r"--data-raw\s+['\"]([^'\"]+)['\"]", curl_command)
        if data_match:
            data = data_match.group(1)

        # 生成Python代码
        code = "import requests\n\n"
        code += f"url = '{url}'\n"
        code += f"headers = {json.dumps(headers, indent=4)}\n"

        if method == 'GET':
            code += "response = requests.get(url, headers=headers)\n"
        elif method == 'POST':
            code += f"data = '{data}'\n" if data else ""
            code += "response = requests.post(url, headers=headers, data=data)\n"
        else:
            code += f"response = requests.request('{method}', url, headers=headers, data=data)\n"

        code += "\nprint(response.text)"
        return code