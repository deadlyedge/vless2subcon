this project is made for fun, and may not have any kind of support.

project code at: https://github.com/deadlyedge/vless2subcon

这个docker将 `vless://` 格式的自建服务器链接添加到已有的clash订阅（或者自建的subconvert docker），在支持vless的clash内核中（如meta内核）实现添加自建服务器。

## 开始之前
准备两个文件：

1： `config.yaml` 应该像下面这个样子
```yaml
subscription_url:  [你的clash订阅地址]
vless_servers:
- vless://big-bad-wolf@199.159.199.73:443?host=hello.kitty.com&path=&type=ws&encryption=none&fp=chrome&security=tls&sni=hello.kitty.com#myHelloKittyVlessServer
```

2： `docker-compose.yml` 应该像下面

```yaml
version: '3.9'
services:
  vless2subcon:
    image: xdream76/vless2subcon
    container_name: vless2subcon
    volumes:
      - $PWD/config.yaml:/code/config.yaml
    ports:
      - 8001:8001  # 曝露端口（随意）:内部端口（不要改动）
    restart: unless-stopped
```
将这两个文件放入某个vps的某个文件夹

## 拉取镜像运行
在上述建立的文件夹中
```bash
docker-compose up -d
```

## 获取你的最终订阅

```http
http(s)://your.vps.address:8001(曝露端口)
```
注意设置vps相应端口防火墙规则

## 如果需要添加自建服务器

需要进行URL编码： https://www.urlencoder.org/

将你的vless服务器连接逐个贴上，用竖线 `|` 隔开，如：
```http
vless://big-bad-wolf@199.159.199.73:443?host=...#myHelloKitty|vless://big-bad-...#myHelloKitty2
```
点击 `ENCODE` 后生成如下：
```http
vless%3A%2F%2Fbig-bad-wolf%40199.159.199.73%3A443%3Fhost%3Dhello.kitty.com%26path%3D%26type%3Dws%26encryption%3Dnone%26fp%3Dchrome%26security%3Dtls%26sni%3Dhello.kitty.com%23myHelloKittyVlessServer%7Cvless%3A%2F%2Fbig-bad-wolf%40199.159.199.73%3A443%3Fhost%3Dhello.kitty.com%26path%3D%26type%3Dws%26encryption%3Dnone%26fp%3Dchrome%26security%3Dtls%26sni%3Dhello.kitty.com%23myHelloKittyVlessServer2
```
在浏览器粘上生成的地址：
```http
http(s)://your.vps.address:8001(曝露端口)/[粘在这里]
```
最后效果如下：
```http
https://your.vps.address:8001/vless%3A%2F%2Fbig-bad-wolf%40199.159.199.73%3A443%3Fhost%3...
```
然后回车即可，

>注意只需添加一次，而且vless链接中最后的 `#给服务器起名` 部分不要重名，添加的vless服务器会被保存到 `config.yaml` 中，以后订阅只需要使用 `https://your.vps.address:8001`

## 关于安全

>当然如果只是按照上述简介，将订阅地址发布在公网上显然是不明智的，所以最好通过nginx之类的服务进行反代并且添加认证。

所以理想的订阅地址最终大概是这个样子：
```http
https://username:password@your.vps.address/
```
配置方法参考 https://developer.aliyun.com/article/278052

## 删除自建服务器

修改vps中一开始建立那个 `config.yaml` 文件
