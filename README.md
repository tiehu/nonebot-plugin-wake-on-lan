<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-wake-on-lan

_✨ Nonebot 局域网唤醒插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/tiehu/nonebot-plugin-wake-on-lan.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-wake-on-lan">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-wake-on-lan.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

一个简单的Nonebot插件，通过向指定子网广播魔术封包来唤醒局域网内的计算机。  

适用于bot和目标设备运行在同一局域网的情况下，例如在局域网下使用Android设备+Termux部署的bot。当然，你也可以把广播IP设置为你的公网IP，然后在你的网关处设置端口转发，将来自指定端口的数据包转发到子网广播地址，以实现用部署在公网服务器上的bot唤醒你自己局域网内的设备。

这是我以前写出来自用的插件，因此很多地方都写得比较随便，请见谅。

## 🧩 特点

- 插件使用基类抽象方法，所以理论上是支持跨平台的。但由于个人精力有限，目前只在Telegram上进行了测试。如果在其他平台上出现使用问题请发issue。
- 细化的权限控制，你可以具体配置哪一名用户拥有对哪一台设备的唤醒权限。
- 可设置宵禁时间，宵禁时间内非插件管理员将无法唤醒设备，以免半夜三更设备突然自己启动这种瘆人情况发生。

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装。

    nb plugin install nonebot-plugin-wake-on-lan

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令。

<details>
<summary>pip</summary>

    pip install nonebot-plugin-wake-on-lan
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_wol"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加以下示例配置，并修改其值。

    #wol
    wol_admin='
    [
        "123456789"
    ]
    '
    wol_data_path="/path/to/data/folder"
    wol_curfew='
    {
        "start_time": [20, 0, 0],
        "end_time": [10, 0, 0]
    }
    '

配置说明如下：
- `wol_admin`是一个列表，应为插件管理员的`用户ID`（不同平台获取用户ID的方式各不相同，请自行查找方法），注意`用户ID`应为**字符串**类型。  
可配置多个插件管理员，如：`["123456789", "987654321"]`

- `wol_data_path`是一个字符串，应为插件的数据存储目录，建议确保指向的目录为空目录。  
**如果你使用Windows系统，请务必注意作为路径分隔符的反斜杠需要再加上一个反斜杠来转义。例如`C:\path\to\data\folder`需要填写成`C:\\path\\to\\data\\folder`。**  
数据存储目录的路径可以是绝对路径，也可以是对于bot入口文件（通常为`bot.py`）所在目录的相对路径。众所周知，相对路径以`.`开头表示，例如`./data`代表你的`bot.py`所在目录下的`data`目录，而`/data`这个绝对路径则代表系统根目录下的`data`目录。

- `wol_curfew`是一个字典，其下的`start_time`和`end_time`都是列表，分别为宵禁的开始时间和结束时间。每个列表内有三个元素，对应时、分和秒，这些元素应为**整数**而非字符串。例如`[19, 30, 15]`代表`19点30分15秒`。  
如果开始时间比结束时间更晚，则会被当做跨日期处理。例如上述示例配置就代表宵禁从晚上20点整开始，到次日上午10点整结束。  
如果你不想设置宵禁时间，请将该配置设置为空字典`{}`（即`wol_curfew={}`），或将宵禁的开始时间与结束时间设置为相同。

## 🎉 使用

如果你不知道什么是Wake-on-LAN，可[查看此处](https://zh.wikipedia.org/wiki/%E7%B6%B2%E8%B7%AF%E5%96%9A%E9%86%92)。  
在使用本插件前，**请先确认你的设备可以被魔术封包唤醒**：  
1.在主板BIOS处打开WOL选项。绝大部分的现代主板都支持该功能，但在设置中的名称有所不同。可能叫做`Remote Wake Up`、`Wake-on-LAN`或`由PCI/PCIE设备唤醒`，如果找不到请善用搜索引擎。  
2.在系统中启用WOL。  
对于Linux系统，可以使用`ethtool -s [网络接口名称] wol g`命令启用WOL，但每次重启系统后WOL可能会被再次禁用。可以将该指令通过systemd等方式加入开机自启项，让其每次开机时都自动执行一次。  
对于Windows系统，在设备管理器里找到你的网卡，双击打开配置界面，在`高级`选项卡中启用`唤醒模式匹配`和`唤醒魔包`，并在`电源管理`选项卡中勾选`允许此设备唤醒计算机`。  
3.使用移动端或网页端工具测试WOL是否能正常使用。

## 📜 指令列表

所有指令都可在群聊或私聊环境中触发，但只有拥有权限的用户才能成功执行。  
参数用方括号标出，所有参数都是不可缺省的必填参数。  
**下方的指令表中没有加上，但你可能需要加上指令前缀（默认为`/`）才能成功执行命令。（如`/wol help`）**

`wol wake [设备名称]`：向指定的设备发送魔术封包来唤醒它。用户必须是插件管理员，或被插件管理员授予对应设备的唤醒权限才可执行该指令。  
`wol device set [设备名称] [广播IP] [MAC地址] [端口号（通常为9）]`：添加或设置一个新的设备到设备列表，已在设备列表中的设备配置将被覆盖（需要插件管理员权限）。  
注意`广播IP`参数填写的是子网广播地址，而不是设备的IP地址。如果你不知道什么是子网广播地址，也可以简单理解为要填写成**你设备的局域网IP地址+最后一段改成255**。例如，假设目标设备的IP地址为`172.16.0.1`，则你应该填写`172.16.0.255`。  
`wol device remove [设备名称]`：将一台设备从设备列表中移除（需要插件管理员权限）。  
`wol device list`：显示当前设备列表。出于隐私保护上的考量，设备列表中将只会打印出设备名称，设备的MAC地址等信息将不会显示。同时，用户必须是插件管理员或拥有任何一台设备的唤醒权限才可执行该指令。  
`wol user add [设备名称] [用户ID]`：授权一名用户唤醒指定设备（需要插件管理员权限）。  
`wol user remove [设备名称] [用户ID]`：将一名用户从指定设备的授权列表中移除（需要插件管理员权限）。  
`wol user list [设备名称]`：打印出拥有指定设备唤醒权限的用户列表（需要插件管理员权限）。  
`wol help`：查看插件帮助信息。