#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests


class Alert:
    def __init__(this, key):
        this.key = key

    def send(self, title, download_url, msg):
        content = {"msg_type": "text", "content": {"text": f"{title}\n下载地址：{download_url}\n{msg}"}}
        requests.post('https://open.feishu.cn/open-apis/bot/v2/hook/%s' % self.key, json=content)


if __name__ == '__main__':
    a = Alert(key="")
