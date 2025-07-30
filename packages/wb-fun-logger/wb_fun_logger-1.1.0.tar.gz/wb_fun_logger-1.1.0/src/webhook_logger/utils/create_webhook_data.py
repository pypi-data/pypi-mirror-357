import requests

from typing import Any, Dict

class WebhookMessager:
    def __init__(self, message_target: str, machine_name: str):
        """
        message_target: 消息发送目标, 例如: feishu
        """
        from webhook_logger.config import get_config
        self.message_target = message_target
        self.machine_name = machine_name
        self.config = get_config()
          
    def __create_data(self, 
                    msg: Any, 
                    user_id: str = None, 
                    is_error: bool = False,
                    error_level: int = 3,
                    machine_name: str = None,
                    ):
        """
        data: 消息数据
        user_id: 用户ID
        is_error: 是否是错误消息
        """
        target_choice = {
            "feishu": self.__create_feishu_data,
        }

        return target_choice[self.message_target](msg, user_id, is_error, error_level, machine_name)

    def __create_feishu_data(self, msg, user_id, is_error, error_level, machine_name):
        
        if is_error:
            return self.__create_feishu_error_data(machine_name=machine_name, msg=msg, error_level=error_level, at_user_id=user_id)
        else:
            return self.__create_feishu_normal_data(machine_name=machine_name, msg=msg, at_user_id=user_id)

    def __create_feishu_error_data(self, machine_name: str, msg: Any, error_level: int, at_user_id: str) -> Dict[str, Any]:
        """
        创建飞书提示数据。

        Args:
            machine_name: 机器名称
            msg: 提示信息
            error_level: 错误等级
            at_user_info: 需要@的用户信息
        """
        error_type_dict = {3: "普通警告", 2: "普通错误", 1: "严重错误", 0: "致命错误"}
        title = error_type_dict.get(error_level, "未知错误等级，检查代码对应部分")
        value_dict = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": f"Machine name: {machine_name} \nMessage: {msg} \n",
                                },
                            ]
                        ],
                    }
                }
            },
        }

        if error_level == 0:

            value_dict["content"]["post"]["zh_cn"]["content"].append(
                [{"tag": "at", "user_id": "all"}]
            )

        elif at_user_id:
            value_dict["content"]["post"]["zh_cn"]["content"].append(
                [{"tag": "at", "user_id": at_user_id}]
            )

        return value_dict

    def __create_feishu_normal_data(self, machine_name: str, msg: Any, at_user_id: str) -> Dict[str, Any]:
        """
        创建飞书提示数据，仅用作内部提示。

        Args:
            machine_name: 机器名称
            msg: 提示信息
            at_user_info: 需要@的用户信息
        """
        value_dict = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "Info",
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": f"Machine name: {machine_name} \nMessage: {msg}",
                                },
                            ]
                        ],
                    }
                }
            },
        }

        if at_user_id:
            value_dict["content"]["post"]["zh_cn"]["content"].append(
                [{"tag": "at", "user_id": at_user_id}]
            )

        return value_dict
    
    def post_data(self, 
                  msg:Any,
                  user_id:str = None,
                  is_error:bool = False,
                  error_level:int = 3,
                  ):
        """
        发送消息
        """
        url = self.config.get("webhook_url", env_var="WEBHOOK_URL")
        machine_name = self.config.get("machine_id", env_var="MACHINE_ID")
        data = self.__create_data(msg=msg, user_id=user_id, is_error=is_error, error_level=error_level, machine_name=machine_name)
        if not url:
            raise ValueError("webhook_url is not set")
        
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise ValueError("Failed to send message")