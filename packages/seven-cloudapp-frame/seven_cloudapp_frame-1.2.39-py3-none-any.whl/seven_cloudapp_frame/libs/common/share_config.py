# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2023-02-09 18:29:31
@LastEditTime: 2025-06-25 11:50:44
@LastEditors: HuangJianYi
:Description: 全局share配置
"""

import json
import threading
from seven_framework import config

_lock = threading.Condition()


def init_config(path):
    """
    :Description: 初始化配置文件
    :param path: 配置文件路径，可使用物理路径或url
    :return: global share_app_config
    :last_editors: HuangJianYi
    """
    if path.lower().find("http://") > -1:
        import requests
        json_str = requests.get(path)
    else:
        with open(path, "r+", encoding="utf-8") as f:
            json_str = f.read()
    global share_app_config
    share_app_config = json.loads(json_str)


def init_config_from_nacos(config_file, config_content, environment):
    """
    :Description: 初始化配置文件
    :param config_file: 配置文件路径，可使用物理路径或url
    :param config_content: 配置内容
    :param environment: 环境标识
    :return: global app_config
    :last_editors: HuangJianYi
    """
    print(f"成功获取nacos配置，并替换本地配置文件{config_file}")

    global share_app_config

    share_app_config = json.loads(config_content)
    # 改写配置share.json只保留nacos键值，其他替换成share_app_config内容。
    with open(config_file, "r+", encoding="utf-8") as f:
        json_str = f.read()
        local_config = json.loads(json_str)
        config_key = "nacos_" + environment
        if config_key in local_config:
            share_app_config[config_key] = local_config[config_key]
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(json.dumps(share_app_config, indent=4, ensure_ascii=False))


def set_value(key, value):
    """
    :Description: 设置一个全局键值配置
    :param key:参数键名
    :param value:参数值
    :return: 无
    :last_editors: HuangJianYi
    """
    _lock.acquire()
    try:
        share_app_config[key] = value
    except:
        raise
    finally:
        _lock.release()


def get_value(key, default_value=None):
    """
    :Description: 获得一个全局变量,不存在则返回默认值
    :param key:参数键名
    :param default_value:获取不到返回的默认值
    :return: 参数值
    :last_editors: HuangJianYi
    """
    config_value = config.get_value(key)
    if config_value == None:
        try:
            _lock.acquire()
            config_value = share_app_config[key]
            if config_value == None:
                config_value = default_value
        except KeyError:
            config_value = default_value
        except NameError:
            config_value = default_value
        finally:
            _lock.release()
    return config_value
