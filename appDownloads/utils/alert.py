#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests


class Alert:
    def __init__(self, group):
        self.group = group

    def send(self, title, download_url, msg):
        msg = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": f"{title}",
                        "content": [
                            [
                                {
                                    "tag": "text",
                                    "text": f"下载地址: {download_url}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": msg
                                }
                            ]
                        ]
                    }
                }
            }
        }

        requests.post(f'https://open.feishu.cn/open-apis/bot/v2/hook/{self.group}', json=msg)


# if __name__ == '__main__':
    # a.send("title", 'download_url', 'msg')
