#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests


class Alert:
    def __init__(this, groupName):
        this.groupName = groupName

    def send(self, title, download_url, msg):
        # content = {
        #     "msgtype": "markdown",
        #     "markdown": {
        #         "content": title +
        #                    "\n## [下载地址 " + download_url + "]( " + download_url + ")" +
        #                    "\n" + msg
        #     }
        # }

        content = {
            "title": (title if self.groupName == '' else self.groupName),
            "users": ["denghaizhu", "zhouweisong", "zhangyahao"],
            "content": '下载地址：%s\n%s' % (download_url, msg),
            "type": "group"
        }
        requests.post('https://alert.shouyouwan.net/feishu/send', json=content)


if __name__ == '__main__':
    a = Alert(key="")
    # a.send("http://192.168.62.75:8000/app/", '描述')
