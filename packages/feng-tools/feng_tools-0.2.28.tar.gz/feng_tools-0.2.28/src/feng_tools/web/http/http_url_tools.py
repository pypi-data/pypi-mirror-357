from urllib.parse import urlparse
import tldextract
import re


def get_hostname_using_urlparse(url) -> tuple[str, int]:
    """使用urllib.parse.urlparse获取主机名"""
    # 确保URL有scheme (http:// 或 https://)
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # 解析URL
    parsed_url = urlparse(url)
    port = 443
    if parsed_url.scheme == 'http':
        port = 80 if parsed_url.port is None else parsed_url.port
    return parsed_url.hostname, port


def get_domain_using_tldextract(url):
    """使用tldextract库获取注册域名"""
    # 安装: pip install tldextract
    result = tldextract.extract(url)
    # 返回注册域名 (example.com)
    return f"{result.domain}.{result.suffix}"


def get_hostname_using_regex(url):
    """使用正则表达式提取主机名"""
    # 确保URL有scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    # 简单的正则表达式匹配主机名
    pattern = r'https?://([^/?#]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None


def get_hostname_with_port(url):
    """获取包含端口号的主机名"""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed_url = urlparse(url)
    if parsed_url.port:
        return f"{parsed_url.hostname}:{parsed_url.port}"
    return parsed_url.hostname


def get_subdomain(url):
    """获取子域名部分"""
    result = tldextract.extract(url)
    # 返回子域名 (www, blog, etc.)
    return result.subdomain


# 测试各种方法
if __name__ == "__main__":
    test_urls = [
        "https://www.example.com/path/to/resource?query=string#fragment",
        "http://example.co.uk",
        "https://subdomain.example.co.uk:8080/path",
        "ftp://ftp.example.com/files",  # 非HTTP协议
        "example.com"  # 没有scheme的URL
    ]

    for url in test_urls:
        print(f"URL: {url}") # https://subdomain.example.co.uk:8080/path
        print(f"主机名 (urlparse): {get_hostname_using_urlparse(url)}") # subdomain.example.co.uk
        print(f"注册域名 (tldextract): {get_domain_using_tldextract(url)}")  # example.co.uk
        print(f"子域名 (tldextract): {get_subdomain(url)}")  # subdomain
        print(f"主机名(含端口): {get_hostname_with_port(url)}") # subdomain.example.co.uk:8080
        print(f"主机名 (regex): {get_hostname_using_regex(url)}") # subdomain.example.co.uk:8080
        print("-" * 50)