from nonebot import on_command, get_driver
from nonebot.adapters import Bot
from nonebot.adapters import Event
from nonebot.plugin import PluginMetadata

import socket
import binascii
import asyncio
import datetime

from .config import Config
from .data import save_json, load_json


plugin_config = Config.parse_obj(get_driver().config)
plugin_data = asyncio.run(load_json())

__plugin_meta__ = PluginMetadata(
    name="局域网唤醒",
    description="通过发送魔术封包唤醒Bot所在局域网内的设备",
    usage="使用“wol help”命令查看说明",
    type="application",
    homepage="https://github.com/tiehu/nonebot-plugin-wol",
    config=Config,
    supported_adapters=None,
)

async def time_check():
    if len(plugin_config.wol_curfew) == 0:
        return True
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(*plugin_config.wol_curfew["start_time"])
    end_time = datetime.time(*plugin_config.wol_curfew["end_time"])
    zero_time = datetime.time(0, 0, 0)
    if start_time == end_time:
        return True
    if start_time > end_time:
        if current_time >= start_time or current_time <= end_time:
            return False
        else:
            return True
    elif start_time <= current_time <= end_time:
        return False
    else:
        return True

@on_command("wol").handle()
async def wol(bot: Bot, event: Event):
    user = event.get_user_id()
    message = event.get_plaintext()
    args = message.split()
    if len(args) <= 1 or args[1] == "help":
        await help(bot, event)
    elif args[1] == "wake":
        await wake(bot, event, user, args)
    elif args[1] == "device":
        if args[2] == "set":
            await device_set(bot, event, user, args)
        elif args[2] == "remove":
            await device_remove(bot, event, user, args)
        elif args[2] == "list":
            await device_list(bot, event, user, args)
    elif args[1] == "user":
        if args[2] == "add":
            await user_add(bot, event, user, args)
        elif args[2] == "remove":
            await user_remove(bot, event, user, args)
        elif args[2] == "list":
            await user_list(bot, event, user, args)
    else:
        await bot.send(event, "参数不正确，请使用wol help查看使用方法。")

async def wake(bot, event, user, args):
    if len(args) != 3:
        await bot.send(event, "参数数量不正确")
        return
    elif not args[2] in plugin_data.keys():
        await bot.send(event, "指定的设备不存在")
        return
    elif not user in plugin_config.wol_admin and not user in plugin_data[args[2]]["user"]:
        await bot.send(event, "权限不足")
        return
    elif not user in plugin_config.wol_admin and not await time_check():
        await bot.send(event, "当前处于宵禁时间内，只有插件管理员有权唤醒设备")
        return
    ip = plugin_data[args[2]]["ip"]
    mac = plugin_data[args[2]]["mac"]
    port = plugin_data[args[2]]["port"]
    pack_data = 'FF' * 6 + str(mac.replace(":", "")) * 16
    send_data = binascii.unhexlify(pack_data)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.sendto(send_data, (ip, port))
    await bot.send(event, "已向目标设备发送魔术封包。")

async def device_set(bot, event, user, args):
    if not user in plugin_config.wol_admin:
        await bot.send(event, "权限不足")
        return
    elif len(args) != 7:
        await bot.send(event, "参数数量不正确")
        return
    port = None
    try:
        port = int(args[6])
    except ValueError:
        await bot.send(event, "无效的端口号")
        return
    new_data = {
        args[3]: {
            "ip": args[4],
            "mac": args[5],
            "port": port,
            "user": []
        }
    }
    plugin_data.update(new_data)
    await save_json(plugin_data)
    await bot.send(event, "操作成功")
    return

async def device_remove(bot, event, user, args):
    if not user in plugin_config.wol_admin:
        await bot.send(event, "权限不足")
        return
    elif len(args) != 4:
        await bot.send(event, "参数数量不正确")
        return
    elif not args[3] in plugin_data.keys():
        await bot.send(event, "指定的设备不存在")
        return
    del plugin_data[args[3]]
    await save_json(plugin_data)
    await bot.send(event, "操作成功")
    return

async def device_list(bot, event, user ,args):
    perm_user = []
    for item in plugin_data.values():
        perm_user = item["user"]
    if not user in perm_user and not user in plugin_config.wol_admin:
        await bot.send(event, "权限不足，你至少要拥有一个设备的唤醒权限才可查看设备列表")
        return
    elif len(args) != 3:
        await bot.send(event, "参数数量不正确")
        return
    elif len(plugin_data) == 0:
        await bot.send(event, "设备列表为空")
        return
    lines = []
    for item in plugin_data.keys():
        lines.append(item)
    text = "\n".join(lines)
    await bot.send(event, text)
    return

async def user_add(bot, event, user, args):
    if not user in plugin_config.wol_admin:
        await bot.send(event, "权限不足")
        return
    elif len(args) != 5:
        await bot.send(event, "参数数量不正确")
        return
    elif not args[3] in plugin_data.keys():
        await bot.send(event, "指定的设备不存在")
        return
    elif args[4] in plugin_data[args[3]]["user"]:
        await bot.send(event, "指定的用户已拥有该设备唤醒权限")
        return
    plugin_data[args[3]]["user"].append(args[4])
    await save_json(plugin_data)
    await bot.send(event, "操作成功！")
    return

async def user_remove(bot, event, user, args):
    if not user in plugin_config.wol_admin:
        await bot.send(event, "权限不足")
        return
    elif len(args) != 5:
        await bot.send(event, "参数数量不正确")
        return
    elif not args[3] in plugin_data.keys():
        await bot.send(event, "指定的设备不存在")
        return
    elif not args[4] in plugin_data[args[3]]["user"]:
        await bot.send(event, "指定的用户没有唤醒该设备的权限")
        return
    plugin_data[args[3]]["user"].remove(args[4])
    await save_json(plugin_data)
    await bot.send(event, "操作成功！")
    return

async def user_list(bot, event, user, args):
    if not user in plugin_config.wol_admin:
        await bot.send(event, "权限不足")
        return
    elif len(args) != 4:
        await bot.send(event, "参数数量不正确")
        return
    elif not args[3] in plugin_data.keys():
        await bot.send(event, "指定的设备不存在")
        return
    elif len(plugin_data[args[3]]["user"]) == 0:
        await bot.send(event, "当前没有任何用户被授权唤醒该设备")
        return
    lines = [f"当前有权限唤醒{args[3]}的用户："]
    for item in plugin_data[args[3]]["user"]:
        lines.append(item)
    text = "\n".join(lines)
    await bot.send(event, text)
    return

async def help(bot, event):
    help_info = """wol命令帮助：
    wol wake [设备名称]
    唤醒目标设备
    wol device set [设备名称] [广播IP] [MAC地址] [端口号（通常为9）]
    添加或设置一台设备用于唤醒（设置已有设备将会覆盖原配置）。
    示例：wol device set my_device 172.16.0.255 1A:2B:3C:4D:5E:6F 9
    wol device remove [设备名称]
    从设备列表中移除指定设备。
    wol device list
    查看当前设备列表。
    wol user add/remove [设备名称] [用户ID]
    授予一位用户指定设备的唤醒权限。
    wol user list [设备名称]
    查看拥有指定设备唤醒权限的用户列表。
    wol help
    查看此帮助信息。
    """
    await bot.send(event, help_info)
    return