# -*- coding: utf-8 -*-
# ----------------------------
# @Author:    影子
# @Software:  PyCharm
# @时间:       2025/6/3 下午3:20
# @项目:       TestProject
# @FileName:  form_data_boundary.py
# ----------------------------
import re
import shlex


def curl_boundary(curl_command):
    """解析 multipart/form-data 类型的 curl 命令，支持多文件上传"""
    parts = shlex.split(curl_command)

    url = None
    headers = {}
    data = ''

    i = 0
    while i < len(parts):
        part = parts[i]
        if part.startswith('http'):
            url = part
        elif part == '-H':
            header_line = parts[i + 1]
            key, val = header_line.split(':', 1)
            headers[key.strip()] = val.strip()
            i += 1
        elif part in ('--data-raw', '--data', '-d'):
            raw_data = parts[i + 1]
            data = raw_data.replace('\\n', '\n').replace('\\r', '\r')
            i += 1
        i += 1

    if not url:
        raise ValueError("在curl命令中找不到URL")

    headers.pop('Content-Type', None)

    # 构建输出字符串
    try:
        file_entries, payload = process_form_data(data)
    except Exception as e:
        raise ValueError(f"form-data 解析失败: {e}")

    code_lines = [
        "import requests\n\n",
        f"url = {repr(url)}\n",
        "headers = {\n"
    ]

    for k, v in headers.items():
        code_lines.append(f"    {repr(k)}: {repr(v)},\n")
    code_lines.append("}\n\n")

    # 动态生成文件句柄部分（with 上下文）
    if file_entries:
        code_lines.append("files = {\n")
        for name, path in file_entries:
            safe_path = repr(path)
            code_lines.append(f"    {repr(name)}: open({safe_path}, 'rb'),\n")
        code_lines.append("}\n\n")

    code_lines.append(f"payload = {repr(payload)}\n")

    code_lines.append("response = requests.post(url, headers=headers, data=payload")
    if file_entries:
        code_lines.append(", files=files")
    code_lines.append(")\n\n")
    code_lines.append("print(response.text)\n")

    return ''.join(code_lines)


def extract_name_and_content(raw_data):
    """提取 multipart/form-data 中的字段名和内容"""
    cleaned_data = raw_data.lstrip('$')
    # 分界符（从原始数据第一行获取，去除可能的冗余）
    boundary = cleaned_data.split('\n')[0].strip()
    # 按分界符分割字段（过滤空字段）
    parts = [part.strip() for part in cleaned_data.split(boundary) if part.strip()]
    result = []

    for part in parts:
        # 替换单个 \n 为双 \n\n，确保 header 和 content 被空行分隔
        part = re.sub(r'(?<!\n)\n(?!\n)', '\n\n', part)
        header_end = re.search(r'\r?\n\r?\n', part)
        if not header_end:
            continue  # 无效字段，跳过

        header = part[:header_end.end()].strip()  # 头部（含 Content-Disposition）
        content = part[header_end.end():].strip()  # 内容（空行后的部分）

        # 提取 name 字段（从 Content-Disposition 头）
        name_match = re.search(r'Content-Disposition:\s*form-data;\s*name\s*=\s*"([^"]+)"', header, re.DOTALL)
        if not name_match:
            continue  # 无 name 字段，跳过
        name = name_match.group(1)

        # 提取 filename（可选，仅文件字段有）
        filename_match = re.search(r'filename\s*=\s*"([^"]+)"', header, re.DOTALL)
        filename = filename_match.group(1) if filename_match else None

        # 保存结果
        result.append({
            "name": name,
            "content": content,
            "filename": filename  # 文件字段才有数据
        })

    return result


def process_form_data(form_data):
    """处理form-data数据，返回 (file_entries, payload)"""
    file_entries = []
    payload = {}

    for field in extract_name_and_content(form_data):
        name = field.get('name')
        content = field.get('content')
        filename = field.get('filename')

        if filename:
            file_entries.append((name, filename))
        else:
            if name is not None and content is not None:
                payload[name] = content

    return file_entries, payload
