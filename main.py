import yaml
import requests
from fastapi import FastAPI
from urllib.parse import urlparse, parse_qs
from fastapi.responses import FileResponse


app = FastAPI()


def read_config(path="config.yaml") -> dict:
    with open(path, "r", encoding="UTF-8") as f:
        return yaml.load(f, Loader=yaml.Loader)


def write_yaml(data: dict, path="output.yaml"):
    with open(path, "w", encoding="UTF-8") as f:
        yaml.dump(data, f, allow_unicode=True)


def trans_url_to_info(url) -> dict:
    server_info = urlparse(url)
    # print(server_info)

    # 展开query parameters并合并到一个字典中
    params = {key: value[0] for key, value in parse_qs(server_info.query).items()}
    params["path"] = "/" if "path" not in params.keys() else params["path"]

    return {
        "name": server_info.fragment,
        "server": server_info.hostname,
        "port": server_info.port,
        "client-fingerprint": params["fp"],
        "type": server_info.scheme,
        "uuid": server_info.username,
        "tls": (params["security"] == "tls"),
        "tfo": False,
        "servername": params["host"],
        "skip-cert-verify": False,
        "network": params["type"],
        "ws-opts": {
            "path": params["path"],
            "headers": {"Host": params["host"]},
        },
    }


@app.get("/{urls:path}")
async def parse_url_data(urls: str = ""):
    # 初始化
    config = read_config()
    try:
        sub_url = config["subscription_url"]
        vless_servers = config["vless_servers"] if config["vless_servers"] else []
    except (AttributeError, TypeError, KeyError):
        """
        检查配置文件 config.yaml
        subscription_url:
        vless_servers:
        """
        sub_url = "https://my.sub.domain"
        vless_servers = []
    servers = []

    # 如果传入了添加的vless server
    if urls:
        for url in urls.split("|"):
            vless_servers.append(url)

    # print(vless_servers)

    # 转换所有的自建vless
    for url in vless_servers:
        # print(url)
        try:
            servers.append(trans_url_to_info(url))
        except KeyError:
            return "订阅解滤器中不包含必要的参数"

    # 读取订阅
    try:
        output = yaml.load(requests.get(sub_url).text, Loader=yaml.Loader)
    except requests.exceptions.ConnectionError:
        config = {
            "subscription_url": "https://my.sub.url.address",
            # "subscription_url": sub_url,
            "vless_servers": vless_servers,
        }
        write_yaml(config, path="config.yaml")
        return "首先在设置文件【config.yaml】中填写订阅转换地址"

    # 插入自建vless
    for index, server in enumerate(servers):
        output["proxies"].insert(index, server)
    for group in output["proxy-groups"]:
        for server in servers:
            group["proxies"].append(server["name"])

    # 保存设置
    config = {
        "subscription_url": sub_url,
        "vless_servers": vless_servers,
    }
    write_yaml(config, path="config.yaml")

    # 写入输出yaml文件
    write_yaml(output, path="output.yaml")

    return FileResponse("output.yaml")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
