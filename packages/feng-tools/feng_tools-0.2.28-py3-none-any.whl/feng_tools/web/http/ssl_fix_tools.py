"""
该工具类主要为了解决requests请求时，cert证书无效的问题
"""
import os
import socket
import ssl

import requests

from feng_tools.base.os.windows import sys_tools
from feng_tools.web.http import http_url_tools


# 方法2:
def export_certificate(web_url:str) -> str:
    """
    获取网站的crt证书并保存
    @param web_url: 网站地址
    @return crt证书地址
    """
    # 创建SSL上下文
    context = ssl.create_default_context()
    hostname, port = http_url_tools.get_hostname_using_urlparse(web_url)
    # 获取证书
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as _sock:
            cert = _sock.getpeercert(True)
    # 保存证书
    crt_file_name = sys_tools.del_special_symbol(hostname)
    cert_path = os.path.join(os.path.dirname(__file__), f'{crt_file_name}.crt')
    with open(cert_path, 'wb') as f:
        f.write(ssl.DER_cert_to_PEM_cert(cert).encode())
    return cert_path


def set_cert_env_variable(web_url:str):
    """为设置cert证书的环境变量"""
    cert_path = export_certificate(web_url)
    # 确保证书文件存在
    if not os.path.exists(cert_path):
        print(f"错误: 证书文件不存在 - {cert_path}")
        return False
    # 设置环境变量指向自定义证书
    os.environ['REQUESTS_CA_BUNDLE'] = cert_path
    os.environ['SSL_CERT_FILE'] = cert_path
    print(f"已设置证书环境变量: {cert_path}")
    return True


def disable_cert_verification():
    """禁用证书验证(不推荐在生产环境使用)"""
    # 禁用证书验证警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # 设置空值以禁用验证
    os.environ['REQUESTS_CA_BUNDLE'] = ''
    os.environ['SSL_CERT_FILE'] = ''
    os.environ['CURL_CA_BUNDLE'] = ''
    print("已禁用SSL证书验证(不推荐在生产环境使用)")

def patch_requests_with_custom_cert(web_url:str):
    """猴子补丁(Monkey Patching) requests"""
    # 保存原始的请求方法
    original_request = requests.request
    def patched_request(method, tmp_url, **kwargs):
        cert_path = export_certificate(web_url)
        # 确保verify参数使用我们的自定义证书
        kwargs.setdefault('verify', cert_path)
        print(f"已使用自定义证书 {cert_path} 修补 requests")
        return original_request(method, tmp_url, **kwargs)
    # 替换原始方法
    requests.request = patched_request
    # 同时修补常用的便捷方法
    requests.get = lambda tmp_url, **kwargs: patched_request('GET', tmp_url, **kwargs)
    requests.post = lambda tmp_url, **kwargs: patched_request('POST', tmp_url, **kwargs)



def create_custom_session(web_url:str):
    """创建自定义会话对象"""
    cert_path = export_certificate(web_url)
    session = requests.Session()
    session.verify = cert_path
    return session

if __name__ == "__main__":
    url = "https://huggingface.co/api/whoami-v2"
    # 设置环境变量(对所有使用requests的库有效)
    # set_cert_env_variable(url)
    # disable_cert_verification()
    # 现在导入并使用第三方库
    try:
        patch_requests_with_custom_cert(url)
        # 使用 certifi 提供的 CA 证书
        response = requests.get(url)
        print(response.json())
        # 使用第三方库的代码
        print("第三方库已使用自定义证书")
    except Exception as e:
        print(f"方法5失败: {e}")
