#!/usr/bin/python
# -*- coding: UTF-8 -*-
import qrcode

img = qrcode.make(data="1111")
# 将二维码保存为图片
with open('test.png', 'wb') as f:
    img.save(f)