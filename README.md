# CQHttp in Docker

**此镜像只适用于插件 2.x 版本，现已移至 `richardchien/cqhttp:legacy`。**

CQHttp in Docker 是基于酷 Q 官方的 [CoolQ/docker-wine-coolq](https://github.com/CoolQ/docker-wine-coolq) 镜像稍加修改而来，在启动时自动安装和启用指定版本或最新版本的 CoolQ HTTP API 插件，并从环境变量读取插件的配置。从而可以一键通过 Wine 在 docker 容器中运行酷Q Air 或 Pro 和 HTTP API 插件。

关于 CoolQ HTTP API 插件，见 [richardchien/coolq-http-api](https://github.com/richardchien/coolq-http-api)。

## 下载使用

```sh
$ docker pull richardchien/cqhttp:legacy
$ docker run -p 9000:9000 -p 5700:5700 richardchien/cqhttp:legacy
```

即可运行一个装有 HTTP API 的 CoolQ 实例。运行后，访问 `http://你的IP:9000` 可以打开一个 VNC 页面，输入 `MAX8chars` 作为密码后即可看到一个 酷 Q Air 已经启动。

上述命令中 9000 端口用于 noVNC，5700 端口是 HTTP API 插件默认的监听端口，可通过环境变量来修改。

**在首次登录后，建议开启「快速登录」选项，以便后续启动和出错重启时可以自动登录。**

## 通过环境变量配置

在创建 docker 容器时，使用以下环境变量，可以调整容器行为。

- `VNC_PASSWD`：设置 VNC 密码。oott123/novnc 镜像说该密码不能超过 8 个字符，但实测超过 8 个字符也没有问题。
- `COOLQ_ACCOUNT`：设置要登录酷 Q 的 QQ 号。在第一次手动登录后，你可以勾选「快速登录」功能以启用自动登录。**此项建议最好设置，因为这关系到容器启动时的自动登录和酷 Q 出错时的自动重启。另外，如果设置此项，需要同时使用 docker 的卷映射功能将容器内的 `/home/user/coolq` 目录持久化（见下面的「注意事项」），否则每次重启容器都会重新下载酷 Q 程序，「快速登录」不会有效果。**
- `COOLQ_URL`：设置下载酷 Q 的地址，默认为 `http://dlsec.cqp.me/cqa-tuling`，即酷 Q Air 图灵版。
- `AUTO_EXIT`：设置为 `1` 会在 HTTP API 插件不可用时退出容器。开启此项后，容器运行过程中，如果直接在 VNC 中重启酷 Q 且恰好酷 Q 需要更新（需较长时间），或者没有设置快速登录的情况下重启酷 Q（再次登录时输入密码需要较长时间），则将会被误判为 HTTP API 不可用，然后退出，所以请视情况开启。
- `CQHTTP_VERSION`：指定要安装的 HTTP API 版本，例如 `2.1.0`（注意只支持选择 2.1.0 或更新版本），如果不指定则默认使用最新版本。
- `CQHTTP_HOST`：指定 HTTP API 监听的 host，例如 `0.0.0.0`。
- HTTP API 插件的其它配置项，均可以和 `CQHTTP_HOST` 一样以 `CQHTTP_` 加配置项名称的大写来设置，具体支持的配置项见 [配置文件说明](https://richardchien.github.io/coolq-http-api/#/Configuration)。

一个示例启动命令如下：

```sh
$ docker run -ti --rm --name cqhttp-test \
             -p 9000:9000 -p 5700:5700 \
             -e CQHTTP_VERSION=2.1.0 \
             -e CQHTTP_HOST=0.0.0.0 \
             -e CQHTTP_POST_URL=http://example.com:8080 \
             -e CQHTTP_SERVE_DATA_FILE=yes \
             richardchien/cqhttp:legacy
```

## 一些注意事项

本镜像会在运行中检测酷 Q 及 HTTP API 的运行状态，如果酷 Q 由于某种原因异常退出，会自动尝试重启酷 Q；当开启了 `AUTO_EXIT` 之后，而如果 HTTP API 插件连续 5 次无法响应，**则会退出容器**，此时建议在启动命令中配置 `--restart=always` 参数。

对于通常使用情况而言，建议将容器的 `/home/user/coolq` 目录映射到持久化的卷或宿主目录，否则每次重启容器都会重新下载酷 Q 和 HTTP API 插件，已登录的账号也会丢失。卷的挂载方法，见 [https://yeasy.gitbooks.io/docker_practice/content/data_management/volume.html](https://yeasy.gitbooks.io/docker_practice/content/data_management/volume.html)。
