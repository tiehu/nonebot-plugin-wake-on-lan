import os
import json
from nonebot import get_driver
from .config import Config

plugin_config = Config.parse_obj(get_driver().config)
data_path = plugin_config.wol_data_path
json_path = os.path.join(data_path, "wol.json")

async def save_json(plugin_data):
    with open(json_path, "w") as json_file:
        json.dump(plugin_data, json_file, indent=4)

async def load_json():
    try:
        with open(json_path, "r") as json_file:
            plugin_data = json.load(json_file)
            return plugin_data
    except FileNotFoundError:
        plugin_data = {}
        await save_json(plugin_data)
        return plugin_data