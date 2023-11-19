from nonebot import logger
from pydantic import BaseModel, validator
import os

class Config(BaseModel):
    wol_admin: list
    wol_data_path: str
    wol_curfew: dict
    
    @validator("wol_admin")
    def check_admin(cls, v):
        if not isinstance(v, list):
            raise ValueError(f"配置项读取错误：“wol_admin”必须是一个列表！")
        elif len(v) == 0:
            raise ValueError(f"配置项读取错误：你至少需要配置一位wol管理员。")    
        for item in v:
            if not isinstance(item, str):
                raise ValueError(f"配置项读取错误：“wol_admin”中的User ID必须为字符串！")
        return v

    @validator("wol_data_path")
    def check_data_path(cls, v):
        if not isinstance(v, str):
            raise ValueError(f"配置项读取错误：“wol_data_path”必须是一个字符串！")
        elif os.path.isfile(v):
            raise ValueError("指定的数据目录路径指向了一个文件而非目录，请填入正确的路径！")
        elif not os.path.exists(v):
            logger.info("指定的数据目录路径不存在，自动创建。")
            try:
                os.makedirs(v)
            except OSError as e:
                raise ValueError(f"创建目录时失败：{e}")
        return v

    @validator("wol_curfew")
    def check_curfew(cls, v):
        if len(v) == 0:
            logger.info("未设置宵禁时间，你可能会希望设置一个宵禁时间以禁止设备在这个时间段内被唤醒。")
            return v
        elif not isinstance(v, dict):
            raise ValueError(f"配置项读取错误：“wol_curfew”必须是一个字典！")
        all_key = ["start_time", "end_time"]
        for key in all_key:
            if not key in v.keys() or len(v[key]) == 0:
                raise ValueError(f"配置项读取错误：配置项“wol_curfew”中缺失“{key}”！如果你不希望设置宵禁时间，请直接把整个“wol_curfew”配置项设置为空字典“{{}}”。")
            elif not isinstance(v[key], list):
                raise ValueError(f"配置项读取错误：配置项“wol_curfew”中的“{key}”必须是一个列表！")
            elif not len(v[key]) == 3:
                raise ValueError(f"配置项读取错误：配置项“wol_curfew”中的“{key}”长度不正确，列表长度必须为3！")
            for item in v[key]:
                if not isinstance(item, int):
                    raise ValueError(f"配置项读取错误：配置项“wol_curfew”中的“{key}”内的所有元素必须为整数！")
        return v