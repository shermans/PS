#!/usr/bin/env python3
import sys
import base64
import urllib.request
import urllib.error
import re
import os

def fetch_content(url):
    """从 URL 获取文本内容，失败返回 None"""
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return resp.read().decode('utf-8')
    except Exception as e:
        print(f"⚠️ 获取 {url} 失败: {e}", file=sys.stderr)
        return None

def is_base64_like(s):
    """粗略判断字符串是否为 Base64 编码"""
    s = s.strip()
    if len(s) % 4 != 0:
        return False
    return bool(re.match(r'^[A-Za-z0-9+/]+=*$', s))

def decode_if_base64(content):
    """如果内容是 Base64 且解码后像节点列表，则返回解码内容，否则原样返回"""
    stripped = content.strip()
    if is_base64_like(stripped):
        try:
            decoded = base64.b64decode(stripped).decode('utf-8')
            if '://' in decoded or '\n' in decoded:
                return decoded
        except Exception:
            pass
    return content

def read_urls_from_file(filename="PSlinks.txt"):
    """从文件中读取非空行作为 URL"""
    if not os.path.exists(filename):
        print(f"❌ 文件 {filename} 不存在！", file=sys.stderr)
        sys.exit(1)
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines

def main():
    # 读取 PSlinks.txt 中的订阅链接
    urls = read_urls_from_file()

    if not urls:
        print("❌ PSlinks.txt 中没有有效的订阅链接。", file=sys.stderr)
        sys.exit(1)

    all_nodes = []
    for url in urls:
        print(f"🔍 正在处理: {url}", file=sys.stderr)
        raw = fetch_content(url)
        if raw is None:
            continue
        decoded = decode_if_base64(raw)
        nodes = [line.strip() for line in decoded.splitlines() if line.strip()]
        all_nodes.extend(nodes)

    if not all_nodes:
        print("❌ 没有获取到任何有效节点。", file=sys.stderr)
        sys.exit(1)

    # 合并节点并编码为 Base64
    combined = '\n'.join(all_nodes)
    b64_output = base64.b64encode(combined.encode('utf-8')).decode('ascii')

    # 写入 PS.txt 文件
    output_file = "PS.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(b64_output)

    print(f"✅ 合并完成！结果已写入 {output_file}", file=sys.stderr)
    print("📄 文件内容如下（同时会显示在控制台）：")
    print(b64_output)   # 也显示出来方便查看

if __name__ == '__main__':
    main()
