# 网络测试 Telegram 机器人

本项目实现了一个 Telegram 机器人，能够通过远程服务器进行网络测试，包括 **Ping 测试** 和 **路由追踪 (NextTrace)**。同时，机器人还提供了管理员命令来管理授权用户和服务器。

---

- 测试demo：[Network Test Bot](https://t.me/linea_network_test_bot)

## 目录

- [功能介绍](#功能介绍)
- [项目结构](#项目结构)
- [前置要求](#前置要求)
- [安装和配置](#安装和配置)
- [如何运行机器人](#如何运行机器人)
- [使用说明](#使用说明)
  - [普通用户功能](#普通用户功能)
  - [管理员功能](#管理员功能)
- [常见问题](#常见问题)
- [后续扩展](#后续扩展)
- [许可协议](#许可协议)

---

## 功能介绍

- **Ping 测试**：向指定目标发送 Ping 请求，统计丢包率和延迟等信息。
- **路由追踪 (NextTrace)**：对目标进行路由追踪，显示网络路径和延迟数据。
- **交互式操作**：通过 Telegram 内联按钮选择服务器、设置测试参数，支持命令式和交互式两种模式。
- **管理员命令**：支持添加/删除授权用户、添加/删除测试服务器，便于管理和维护。

---

## 项目结构

本项目采用模块化设计，代码被拆分成多个文件，每个文件负责不同的功能。主要目录和文件说明如下：

```
mybot/
├── config.py         # 配置加载和保存（包括机器人 token、用户列表、服务器列表）
├── state.py          # 存储运行时的全局状态变量（如用户操作数据、速率限制信息）
├── utils.py          # 常用辅助函数（日志、权限检查、消息删除、进度提示等）
├── network.py        # 网络测试相关函数（Ping/NextTrace 命令的解析与格式化）
├── tasks.py          # 后台任务（执行长时间运行的网络测试，并更新进度提示）
├── commands.py       # Telegram 命令处理函数（用户和管理员命令）
├── handlers.py       # 消息和按钮回调处理函数（交互式输入的处理）
└── bot.py            # 主入口文件，构建 Telegram Bot 应用并注册所有处理器
```

你可以直接参考或修改这些文件，也可以根据需要扩展新的功能。

---

## 前置要求

- **Python 版本**：建议使用 Python 3.10 或更高版本。
- **依赖库**：
  - [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
  - [paramiko](https://github.com/paramiko/paramiko)

---

## 安装和配置

### 1. 克隆项目

在命令行中运行以下命令将项目克隆到本地（假设你已经安装了 Git）：

```bash
git clone https://github.com/Sanite-Ava/Network_Test_Bot.git
cd Network_Test_Bot
```

### 2. 配置 `config.json`

在项目根目录下创建一个 `config.json` 文件，该文件用于配置机器人 token、管理员、授权用户以及服务器信息。下面提供一个示例配置：

```json
{
  "TELEGRAM_BOT_TOKEN": "你的Telegram Bot Token",
  "ADMIN_USERS": [123456789],
  "AUTHORIZED_USERS": [123456789, 987654321],
  "SERVERS": [
    {
      "name": "服务器1",
      "host": "192.168.1.100",
      "port": 22,
      "username": "root",
      "password": "yourpassword"
    },
    {
      "name": "服务器2",
      "host": "example.com",
      "port": 22,
      "username": "user",
      "password": "yourpassword"
    }
  ]
}
```

**注意：**
- 替换 `"你的Telegram Bot Token"` 为你从 [BotFather](https://t.me/BotFather) 获取的实际 token。
- `ADMIN_USERS` 数组中填写管理员的 Telegram 用户 ID（数字）。
- `AUTHORIZED_USERS` 数组中填写允许使用该机器人的用户 ID。
- `SERVERS` 数组中填写你拥有 SSH 登录权限的服务器信息。

### 3. 安装依赖库

建议使用 `pip` 安装依赖：

```bash
pip install python-telegram-bot paramiko
```

你也可以使用 [virtualenv](https://docs.python-guide.org/dev/virtualenvs/) 创建虚拟环境，然后安装依赖。

---

### 4. 如需使用 `/nexttrace` 命令 (可选)

进入被控机SSH安装NextTrace工具：

```bash
curl nxtrace.org/nt |bash
```

---

## 如何运行机器人

在项目根目录下，运行主入口文件 `bot.py`：

```bash
python bot.py
```

如果一切配置正确，你的 Telegram 机器人就会开始轮询更新，等待用户命令。

---

## 使用说明

### 普通用户功能

1. **启动机器人**  
   在 Telegram 中向你的机器人发送 `/start` 命令，机器人会回复欢迎信息和使用说明。

2. **Ping 测试**  
   - 命令式：  
     直接发送 `/ping 8.8.8.8 4`，其中 `8.8.8.8` 是目标 IP，`4` 是 Ping 次数（默认为 4）。
   - 交互式：  
     只发送 `/ping`，机器人会引导你选择测试服务器，然后提示你输入目标 IP 或域名，并选择 Ping 次数。

3. **路由追踪 (NextTrace)**  
   - 命令式：  
     直接发送 `/nexttrace google.com`，机器人会引导你选择测试服务器，若目标不是有效 IP，则会提示你选择 IPv4 或 IPv6 模式。
   - 交互式：  
     只发送 `/nexttrace`，机器人会引导你选择服务器，然后提示你输入目标，最后根据目标类型选择执行方式。

### 管理员功能

1. **添加授权用户**  
   `/adduser 111222333`  
   将用户 ID 为 `111222333` 的用户加入授权列表。

2. **删除授权用户**  
   `/rmuser 111222333`  
   将用户 ID 为 `111222333` 的用户从授权列表中移除。

3. **添加测试服务器**  
   `/addserver 服务器3 example.com 22 user password`  
   添加新的服务器信息。

4. **删除测试服务器**  
   `/rmserver 服务器3`  
   删除名称为“服务器3”的服务器信息。

---

## 鸣谢

感谢 [NextTrace](https://github.com/nxtrace/NTrace-core) 提供的 NextTrace 工具，以及本项目引用的其他开源项目。

---

## 许可协议

本项目采用 [MIT 许可协议](LICENSE)。

