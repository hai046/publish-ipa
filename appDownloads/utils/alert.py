#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests


class Alert:
    def __init__(this, key):
        this.key = key

    def send(self, title, download_url, msg):
        content = {
            "msgtype": "markdown",
            "markdown": {
                "content": title +
                           "\n## [下载地址 " + download_url + "]( " + download_url + ")" +
                           "\n" + msg
            }
        }
        requests.post('https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=%s' % self.key, json=content)


if __name__ == '__main__':
    a = Alert(key="")
    # a.send("http://192.168.62.75:8000/app/", '描述')
