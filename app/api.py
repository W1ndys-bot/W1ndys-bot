# api.py

import json
import logging
import sqlite3
from datetime import datetime

from config import *

SWITCH_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "Switch",
)


# 检查是否是群主
def is_group_owner(role):
    return role == "owner"


# 检查是否是管理员
def is_group_admin(role):
    return role == "admin"


# 检查是否有权限（管理员、群主或root管理员）
def is_authorized(role, user_id):
    is_admin = is_group_admin(role)
    is_owner = is_group_owner(role)
    return (is_admin or is_owner) or (user_id in owner_id)


# 初始化开关数据库
def init_switch_database(group_id):
    if not os.path.exists(SWITCH_DB_PATH):
        os.makedirs(SWITCH_DB_PATH)

    db_path = os.path.join(SWITCH_DB_PATH, f"switch.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS switches (
                group_id TEXT NOT NULL UNIQUE,
                switch_name TEXT NOT NULL,
                status INTEGER NOT NULL
            )
        """
    )

    conn.commit()
    conn.close()


# 发送私聊消息，解析cq码
async def send_private_msg(websocket, user_id, content):
    message = {
        "action": "send_private_msg",
        "params": {"user_id": user_id, "message": content},
        "echo": "send_private_msg",
    }
    await websocket.send(json.dumps(message))
    logging.info(f"[API]已发送消息到用户 {user_id}")


# 发送私聊消息，不解析cq码
async def send_private_msg_no_cq(websocket, user_id, content, auto_escape=True):
    message = {
        "action": "send_private_msg",
        "params": {"user_id": user_id, "message": content, "auto_escape": auto_escape},
        "echo": "send_private_msg_no_cq",
    }
    await websocket.send(json.dumps(message))
    logging.info(f"[API]已发送消息到用户 {user_id}")


# 发送私聊消息，并获取消息ID
async def send_private_msg_with_reply(websocket, user_id, content):
    try:
        message = {
            "action": "send_private_msg",
            "params": {"user_id": user_id, "message": content},
            "echo": "send_private_msg_with_reply",
        }
        await websocket.send(json.dumps(message))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("echo") == "send_private_msg_with_reply":
                message_id = response_data.get("data", {}).get("message_id")
                logging.info(f"[API]已发送消息到用户 {user_id}，消息ID: {message_id}")
                return message_id
    except Exception as e:
        logging.error(f"[API]发送私聊消息失败: {e}")


# 发送群消息
async def send_group_msg(websocket, group_id, content):
    try:
        message = {
            "action": "send_group_msg",
            "params": {"group_id": group_id, "message": content},
            "echo": "send_group_msg",
        }
        await websocket.send(json.dumps(message))
        logging.info(f"[API]已发送群消息到群 {group_id}")
    except Exception as e:
        logging.error(f"[API]发送群消息失败: {e}")


# 发送群消息并获取消息ID
async def send_group_msg_with_reply(websocket, group_id, content):
    try:
        message = {
            "action": "send_group_msg",
            "params": {"group_id": group_id, "message": content},
            "echo": "send_group_msg_with_reply",
        }
        await websocket.send(json.dumps(message))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("echo") == "send_group_msg_with_reply":
                message_id = response_data.get("data", {}).get("message_id")
                logging.info(f"[API]已发送群消息到群 {group_id}，消息ID: {message_id}")
                return message_id
    except Exception as e:
        logging.error(f"[API]发送群消息（带回复）失败: {e}")
        return None


# 给群分享推荐好友
async def send_ArkSharePeer_group(websocket, user_id, group_id):
    try:
        message = {
            "action": "ArkSharePeer",
            "params": {"user_id": str(user_id)},
            "echo": "send_ArkSharePeer_group",
        }
        await websocket.send(json.dumps(message))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("echo") == "send_ArkSharePeer_group":
                data = response_data.get("data", {}).get("arkMsg")
                await send_json_msg_group(websocket, group_id, data)
                break
    except Exception as e:
        logging.error(f"[API]发送推荐好友失败: {e}")


# 给群分享加群卡片
async def send_ArkShareGroupEx_group(websocket, group_id, target_group_id):
    try:
        message = {
            "action": "ArkShareGroupEx",
            "params": {"group_id": str(group_id)},
            "echo": "send_ArkShareGroupEx_group",
        }
        await websocket.send(json.dumps(message))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("echo") == "send_ArkShareGroupEx_group":
                data = response_data.get("data")
                await send_json_msg_group(websocket, target_group_id, data)
                break
    except Exception as e:
        logging.error(f"[API]发送加群卡片失败: {e}")


# 给私聊分享加群卡片
async def send_ArkShareGroupEx_private(websocket, user_id):
    try:
        message = {
            "action": "ArkShareGroupEx",
            "params": {"user_id": str(user_id)},
            "echo": "send_ArkShareGroupEx_private",
        }
        await websocket.send(json.dumps(message))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("echo") == "send_ArkShareGroupEx_private":
                data = response_data.get("data")
                await send_json_msg_private(websocket, user_id, data)
                break
    except Exception as e:
        logging.error(f"[API]发送加群卡片失败: {e}")


# 给私聊分享推荐好友
async def send_ArkSharePeer_private(websocket, user_id):
    try:
        message = {
            "action": "ArkSharePeer",
            "params": {"user_id": str(user_id)},
            "echo": "send_ArkSharePeer_private",
        }
        await websocket.send(json.dumps(message))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("echo") == "send_ArkSharePeer_private":
                data = response_data.get("data", {}).get("arkMsg")
                await send_json_msg_private(websocket, user_id, data)
                break
    except Exception as e:
        logging.error(f"[API]发送推荐好友失败: {e}")


# 向群发送JSON消息
async def send_json_msg_group(websocket, group_id, data):
    try:
        message = {
            "type": "json",
            "data": {"data": data},
            "echo": "send_json_msg_group",
        }  # 注意这边两层data，详情可见https://github.com/botuniverse/onebot-11/blob/master/message/segment.md#json-%E6%B6%88%E6%81%AF
        await send_group_msg(websocket, group_id, message)
    except Exception as e:
        logging.error(f"[API]发送JSON消息失败: {e}")


# 向私聊发送JSON消息
async def send_json_msg_private(websocket, user_id, data):
    try:
        message = {
            "type": "json",
            "data": {"data": data},
            "echo": "send_json_msg_private",
        }
        await send_private_msg(websocket, user_id, message)
    except Exception as e:
        logging.error(f"[API]发送JSON消息失败: {e}")


# 发送消息
async def send_msg(websocket, message_type, user_id, group_id, message):
    message = {
        "action": "send_msg",
        "params": {
            "message_type": message_type,
            "user_id": user_id,
            "group_id": group_id,
            "message": message,
        },
        "echo": "send_msg",
    }
    await websocket.send(json.dumps(message))
    logging.info(f"[API]已发送消息: {message}")


# 发送合并转发消息
async def send_forward_msg(websocket, group_id, content):
    message = {
        "action": "send_forward_msg",
        "params": {"group_id": group_id, "message": content},
        "echo": "send_forward_msg",
    }
    await websocket.send(json.dumps(message))
    logging.info(f"[API]已发送合并转发消息: {content}")


# 撤回消息
async def delete_msg(websocket, message_id):
    delete_msg = {
        "action": "delete_msg",
        "params": {"message_id": message_id},
        "echo": "delete_msg",
    }
    await websocket.send(json.dumps(delete_msg))


# 获取消息
async def get_msg(websocket, message_id):
    get_msg = {
        "action": "get_msg",
        "params": {"message_id": message_id},
        "echo": "get_msg",
    }
    await websocket.send(json.dumps(get_msg))
    logging.info(f"[API]已获取消息 {message_id}。")


# 获取合并转发消息
async def get_forward_msg(websocket, id):
    get_forward_msg = {
        "action": "get_forward_msg",
        "params": {"message_id": id},
        "echo": "get_forward_msg",
    }
    await websocket.send(json.dumps(get_forward_msg))
    logging.info(f"[API]已获取合并转发消息 {id}。")


# 发送好友赞
async def send_like(websocket, user_id, times):
    like_msg = {
        "action": "send_like",
        "params": {"user_id": user_id, "times": times},
        "echo": "send_like",
    }
    await websocket.send(json.dumps(like_msg))
    logging.info(f"[API]已发送好友赞 {user_id} {times} 次。")


# 群组踢人
async def set_group_kick(websocket, group_id, user_id):
    kick_msg = {
        "action": "set_group_kick",
        "params": {"group_id": group_id, "user_id": user_id},
        "echo": "set_group_kick",
    }
    await websocket.send(json.dumps(kick_msg))


# 群组单人禁言
async def set_group_ban(websocket, group_id, user_id, duration):
    ban_msg = {
        "action": "set_group_ban",
        "params": {"group_id": group_id, "user_id": user_id, "duration": duration},
        "echo": "set_group_ban",
    }
    await websocket.send(json.dumps(ban_msg))
    if duration == 0:
        logging.info(f"[API]执行解除 [CQ:at,qq={user_id}] 禁言。")
    else:
        logging.info(f"[API]执行禁言 [CQ:at,qq={user_id}] {duration} 秒。")


# 群组匿名用户禁言
async def set_group_anonymous_ban(websocket, group_id, anonymous_flag, duration):
    anonymous_ban_msg = {
        "action": "set_group_anonymous_ban",
        "params": {"group_id": group_id, "flag": anonymous_flag, "duration": duration},
        "echo": "set_group_anonymous_ban",
    }
    await websocket.send(json.dumps(anonymous_ban_msg))
    if duration == 0:
        logging.info(f"[API]已解除 [CQ:anonymous,flag={anonymous_flag}] 禁言。")
        message = f"已解除 [CQ:anonymous,flag={anonymous_flag}] 禁言。"
    else:
        logging.info(f"[API]已禁止匿名用户 {anonymous_flag} {duration} 秒。")
        message = f"已禁止匿名用户 {anonymous_flag} {duration} 秒。"
    await send_group_msg(websocket, group_id, message)


# 群组全员禁言
async def set_group_whole_ban(websocket, group_id, enable):
    whole_ban_msg = {
        "action": "set_group_whole_ban",
        "params": {"group_id": group_id, "enable": enable},
        "echo": "set_group_whole_ban",
    }
    await websocket.send(json.dumps(whole_ban_msg))
    logging.info(f"[API]已{'开启' if enable else '解除'}群 {group_id} 的全员禁言。")
    await send_group_msg(
        websocket,
        group_id,
        f"已{'开启' if enable else '解除'}群 {group_id} 的全员禁言。",
    )


# 群组设置管理员
async def set_group_admin(websocket, group_id, user_id, enable):
    admin_msg = {
        "action": "set_group_admin",
        "params": {"group_id": group_id, "user_id": user_id, "enable": enable},
        "echo": "set_group_admin",
    }
    await websocket.send(json.dumps(admin_msg))
    logging.info(
        f"已{'授予' if enable else '解除'}群 {group_id} 的管理员 {user_id} 的权限。"
    )


# 群组匿名
async def set_group_anonymous(websocket, group_id, enable):
    anonymous_msg = {
        "action": "set_group_anonymous",
        "params": {"group_id": group_id, "enable": enable},
        "echo": "set_group_anonymous",
    }
    await websocket.send(json.dumps(anonymous_msg))
    logging.info(f"[API]已{'开启' if enable else '关闭'}群 {group_id} 的匿名。")


# 设置群名片（群备注）
async def set_group_card(websocket, group_id, user_id, card):
    card_msg = {
        "action": "set_group_card",
        "params": {"group_id": group_id, "user_id": user_id, "card": card},
        "echo": "set_group_card",
    }
    await websocket.send(json.dumps(card_msg))
    logging.info(f"[API]已设置群 {group_id} 的用户 {user_id} 的群名片为 {card}。")


# 设置群名
async def set_group_name(websocket, group_id, group_name):
    name_msg = {
        "action": "set_group_name",
        "params": {"group_id": group_id, "group_name": group_name},
        "echo": "set_group_name",
    }
    await websocket.send(json.dumps(name_msg))
    logging.info(f"[API]已设置群 {group_id} 的群名为 {group_name}。")


# 退出群组
async def set_group_leave(websocket, group_id, is_dismiss):
    leave_msg = {
        "action": "set_group_leave",
        "params": {"group_id": group_id, "is_dismiss": is_dismiss},
        "echo": "set_group_leave",
    }
    await websocket.send(json.dumps(leave_msg))
    logging.info(f"[API]已退出群 {group_id}。")


# 设置群组专属头衔
async def set_group_special_title(
    websocket, group_id, user_id, special_title, duration
):
    special_title_msg = {
        "action": "set_group_special_title",
        "params": {
            "group_id": group_id,
            "user_id": user_id,
            "special_title": special_title,
            "duration": duration,
        },
        "echo": "set_group_special_title",
    }
    await websocket.send(json.dumps(special_title_msg))
    logging.info(
        f"[API]已设置群 {group_id} 的用户 {user_id} 的专属头衔为 {special_title}。"
    )


# 处理加好友请求
async def set_friend_add_request(websocket, flag, approve):
    request_msg = {
        "action": "set_friend_add_request",
        "params": {"flag": flag, "approve": approve},
        "echo": "set_friend_add_request",
    }
    await websocket.send(json.dumps(request_msg))
    logging.info(f"[API]已{'同意' if approve else '拒绝'}好友请求。")


# 处理加群请求／邀请
async def set_group_add_request(websocket, flag, type, approve, reason):
    request_msg = {
        "action": "set_group_add_request",
        "params": {"flag": flag, "type": type, "approve": approve, "reason": reason},
        "echo": "set_group_add_request",
    }
    await websocket.send(json.dumps(request_msg))
    logging.info(f"[API]已{'同意' if approve else '拒绝'}群 {type} 请求。")


# 获取群历史消息，注意count是int类型
async def get_group_msg_history(websocket, group_id, count):
    history_msg = {
        "action": "get_group_msg_history",
        "params": {"group_id": group_id, "count": count},
        "echo": "get_group_msg_history",
    }
    await websocket.send(json.dumps(history_msg))
    while True:
        response = await websocket.recv()
        response_data = json.loads(response)
        if response_data.get("echo") == "get_group_msg_history":
            logging.info(f"[API]已获取群 {group_id} 的历史消息 {count} 条。")
            return response_data


# 获取登录号信息
async def get_login_info(websocket):
    login_info_msg = {
        "action": "get_login_info",
        "params": {},
        "echo": "get_login_info",
    }
    await websocket.send(json.dumps(login_info_msg))
    logging.info("已获取登录号信息。")


# 获取陌生人信息
async def get_stranger_info(websocket, user_id, no_cache=False):
    try:
        stranger_info_msg = {
            "action": "get_stranger_info",
            "params": {"user_id": user_id, "no_cache": no_cache},
            "echo": "get_stranger_info",
        }
        await websocket.send(json.dumps(stranger_info_msg))
        while True:
            response = await websocket.recv()
            response_data = json.loads(response)
            if response_data.get("echo") == "get_stranger_info":
                logging.info(f"[API]已获取陌生人 {user_id} 信息。")
                return response_data.get("data", {})
    except Exception as e:
        logging.error(f"获取陌生人信息失败: {e}")
        return {}


# 获取好友列表
async def get_friend_list(websocket):
    friend_list_msg = {
        "action": "get_friend_list",
        "params": {},
        "echo": "get_friend_list",
    }
    await websocket.send(json.dumps(friend_list_msg))
    logging.info("已获取好友列表。")


# 获取群信息
async def get_group_info(websocket, group_id):
    group_info_msg = {
        "action": "get_group_info",
        "params": {"group_id": group_id},
        "echo": "get_group_info",
    }
    await websocket.send(json.dumps(group_info_msg))
    logging.info(f"[API]已获取群 {group_id} 信息。")


# 获取群列表
async def get_group_list(websocket):
    group_list_msg = {
        "action": "get_group_list",
        "params": {},
        "echo": "get_group_list",
    }
    await websocket.send(json.dumps(group_list_msg))
    logging.info("已获取群列表。")


# 获取群成员信息
async def get_group_member_info(websocket, group_id, user_id, no_cache=False):
    group_member_info_msg = {
        "action": "get_group_member_info",
        "params": {"group_id": group_id, "user_id": user_id, "no_cache": no_cache},
        "echo": "get_group_member_info",
    }
    await websocket.send(json.dumps(group_member_info_msg))
    while True:
        response = await websocket.recv()
        response_data = json.loads(response)
        if response_data.get("echo") == "get_group_member_info":
            logging.info(f"[API]已获取群 {group_id} 的用户 {user_id} 信息。")
            return response_data


# 获取群成员入群时间戳并转换为日期时间
def get_group_member_join_time(group_id, user_id, group_member_info):
    join_time = group_member_info.get("data", {}).get("join_time", 0)
    # 将时间戳转换为日期时间
    join_time_datetime = datetime.fromtimestamp(join_time)
    logging.info(
        f"[API]已获取群 {group_id} 的用户 {user_id} 入群时间戳: {join_time}, 转换后时间: {join_time_datetime}"
    )
    return join_time_datetime


# 获取群成员列表
async def get_group_member_list(websocket, group_id, no_cache=False):
    group_member_list_msg = {
        "action": "get_group_member_list",
        "params": {"group_id": group_id},
        "echo": "get_group_member_list",
    }
    await websocket.send(json.dumps(group_member_list_msg))
    while True:
        response = await websocket.recv()
        response_data = json.loads(response)
        if response_data.get("echo") == "get_group_member_list":
            logging.info(f"[API]已获取群 {group_id} 的成员列表。")
            return response_data.get("data", [])


# 获取群成员列表返回QQ号数组
async def get_group_member_list_qq(websocket, group_id):
    group_member_list = await get_group_member_list(websocket, group_id)
    logging.info(f"[API]已获取群 {group_id} 的成员列表QQ号数组。")
    return [member.get("user_id") for member in group_member_list]


# 获取群荣誉信息
async def get_group_honor_info(websocket, group_id, type):
    honor_info_msg = {
        "action": "get_group_honor_info",
        "params": {"group_id": group_id, "type": type},
        "echo": "get_group_honor_info",
    }
    await websocket.send(json.dumps(honor_info_msg))
    logging.info(f"[API]已获取群 {group_id} 的 {type} 荣誉信息。")


# 获取 Cookies
async def get_cookies(websocket):
    cookies_msg = {"action": "get_cookies", "params": {}, "echo": "get_cookies"}
    await websocket.send(json.dumps(cookies_msg))
    logging.info("已获取 Cookies。")


# 获取 CSRF Token
async def get_csrf_token(websocket):
    csrf_token_msg = {
        "action": "get_csrf_token",
        "params": {},
        "echo": "get_csrf_token",
    }
    await websocket.send(json.dumps(csrf_token_msg))
    logging.info("已获取 CSRF Token。")


# 获取 QQ 相关接口凭证
async def get_credentials(websocket):
    credentials_msg = {
        "action": "get_credentials",
        "params": {},
        "echo": "get_credentials",
    }
    await websocket.send(json.dumps(credentials_msg))
    logging.info("已获取 QQ 相关接口凭证。")


# 获取语音
async def get_record(websocket, file, out_format, full_path):
    record_msg = {
        "action": "get_record",
        "params": {"file": file, "out_format": out_format, "full_path": full_path},
        "echo": "get_record",
    }
    await websocket.send(json.dumps(record_msg))
    logging.info(f"[API]已获取语音 {file}。")


# 获取图片
async def get_image(websocket, file, out_format, full_path):
    image_msg = {
        "action": "get_image",
        "params": {"file": file, "out_format": out_format, "full_path": full_path},
        "echo": "get_image",
    }
    await websocket.send(json.dumps(image_msg))
    logging.info(f"[API]已获取图片 {file}。")


# 检查是否可以发送图片
async def can_send_image(websocket):
    can_send_image_msg = {
        "action": "can_send_image",
        "params": {},
        "echo": "can_send_image",
    }
    await websocket.send(json.dumps(can_send_image_msg))
    logging.info("已检查是否可以发送图片。")


# 检查是否可以发送语音
async def can_send_record(websocket):
    can_send_record_msg = {
        "action": "can_send_record",
        "params": {},
        "echo": "can_send_record",
    }
    await websocket.send(json.dumps(can_send_record_msg))
    logging.info("已检查是否可以发送语音。")


# 获取运行状态
async def get_status(websocket):
    status_msg = {"action": "get_status", "params": {}, "echo": "get_status"}
    await websocket.send(json.dumps(status_msg))
    logging.info("已获取运行状态。")


# 获取版本信息
async def get_version_info(websocket):
    version_info_msg = {
        "action": "get_version_info",
        "params": {},
        "echo": "get_version_info",
    }
    await websocket.send(json.dumps(version_info_msg))
    logging.info("已获取版本信息。")


# 重启 OneBot 实现
async def set_restart(websocket, delay=0):
    restart_onebot_msg = {
        "action": "set_restart",
        "params": {"delay": delay},
        "echo": "set_restart",
    }
    await websocket.send(json.dumps(restart_onebot_msg))
    logging.info("已重启 OneBot 实现。")


# 清理缓存
async def clean_cache(websocket):
    clean_cache_msg = {"action": "clean_cache", "params": {}, "echo": "clean_cache"}
    await websocket.send(json.dumps(clean_cache_msg))
    logging.info("已清理缓存。")


######## 下面是NapCatQQ的扩展API


# 发送表情回应
# https://bot.q.qq.com/wiki/develop/api-v2/openapi/emoji/model.html#/EmojiType
async def set_msg_emoji_like(websocket, message_id, emoji_id):
    set_msg_emoji_like_msg = {
        "action": "set_msg_emoji_like",
        "params": {"message_id": message_id, "emoji_id": emoji_id},
        "echo": "set_msg_emoji_like",
    }
    await websocket.send(json.dumps(set_msg_emoji_like_msg))
    logging.info(f"[API]已发送表情回应 {message_id} {emoji_id}。")
