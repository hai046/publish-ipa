#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import plistlib
import shutil
import time
import zipfile

import qrcode
from django import forms
from django.http import JsonResponse

from appDownloads.settings import IOS_PLIST_DOMAIN
from appDownloads.utils.alert import Alert
from appDownloads.utils.ipin import updatePNG

base_dir = "downloads"


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


from django.shortcuts import render
from appDownloads.models import AppInfo


def check(request_body, filed):
    if filed not in request_body:
        return None, "必须包含字段，%s" % filed

    return request_body[filed], None


def result_json_err(err):
    return JsonResponse({"code": 500, "message": err})
    pass


def result_json_ok(data):
    return JsonResponse({"code": 200, "message": 'OK', 'data': data})
    pass


def index(request):
    context = {'apps': AppInfo.objects.all()}
    return render(request, 'index.html', context)


def app(request, env, identifier):
    context = {'apps': AppInfo.objects.filter(identifier=identifier, env=env)}
    return render(request, 'index.html', context)


def generatep12(app, app_file, domain_url, version, prefix_name):
    """
    生成iOS下载plist文件
    :param app:
    :param app_file:
    :param domain_url:
    :param version:
    :return:
    """
    app.download_url = "%s/%s" % (domain_url, app_file)
    p12_path = os.path.join(base_dir, "%s_%s.plist" % (prefix_name, app.identifier))
    with open(p12_path, "wb") as fp:
        p12 = {
            "items": [{"assets": [{"kind": "software-package", "url": app.download_url},
                                  {"kind": "display-image", "url": app.display_image},
                                  {"kind": "full-size-image", "url": app.display_image}],
                       "metadata": {"bundle-identifier": app.identifier,
                                    "bundle-version": version,
                                    "kind": "software",
                                    "title": app.name,
                                    }}]
        }
        plistlib.dump(p12, fp)
    return p12_path
    pass


def parse_ipa(file, domain_url, order_id):
    azip = zipfile.ZipFile(file)

    # 返回所有文件夹和文件
    for path in azip.namelist():
        if str(path).endswith(".app/Info.plist"):
            print("查找到ipa信息文件，开始解析：", path)
            with azip.open(path) as f:
                plist = plistlib.load(f)
                app = AppInfo()
                app.name = plist.get('CFBundleDisplayName')
                app.identifier = plist.get('CFBundleIdentifier')
                version = plist.get('CFBundleShortVersionString')
                icon_des = "downloads/no_icon.png"

                plist_icons = plist.get('CFBundleIcons')
                if plist_icons is not None:
                    icons = plist_icons['CFBundlePrimaryIcon']['CFBundleIconFiles']
                    if len(icons) > 0:
                        icon = icons[len(icons) - 1]
                        icon_path = None
                        for p in azip.namelist():
                            if icon in p:
                                # print("icon=", icon, p)
                                icon_path = p
                        ext = ""
                        if "." in str(icon_path):
                            items = str(icon_path).split('.')
                            ext = items[len(items) - 1]
                        icon_des = '%s/%s.%s' % (base_dir, app.identifier, ext)
                        print(icon_des)
                        azip.extract(icon_path, base_dir)
                        shutil.move(os.path.join(base_dir, icon_path), icon_des)
                        # 因为iOS png是有损压缩的，还原一下png图片
                        print(updatePNG(icon_des))
                app.desc = "大小：%.02d MB\n版本：%s" % (os.path.getsize(file) / float(1024 * 1024), version)
                app.display_image = "%s/%s" % (domain_url, icon_des)
                plist = generatep12(app, file, IOS_PLIST_DOMAIN, version, order_id)

                # plist = generatep12(app, upload_file, domain_url)
                # 修改成plist
                if not IOS_PLIST_DOMAIN.startswith("https"):
                    raise Exception("苹果下载的plist必须是https")
                app.download_url = "%s/%s" % (IOS_PLIST_DOMAIN, plist)
                return app
    return None
    pass


# key可以换成你自己的机器人


def upload(request, env):
    if request.method != "POST":
        return result_json_err("只支持post方法")
    if 'key' in request.POST:
        key = request.POST['key']
    else:
        return result_json_err("param key is miss ")
    if 'msg' in request.POST:
        msg = f"\n{request.POST['msg']}"
    else:
        msg = ""
    alert = Alert(key)
    file_obj = request.FILES.get('file')
    if file_obj:
        # domain_url = '{scheme}://{host}'.format(
        #     scheme=request.scheme,
        #     host=request.get_host()
        # )
        #
        # 这个在开发情况下， 请修改自己的域名或者ip，这个不重要，关键的是后面plist必须是https
        domain_url = IOS_PLIST_DOMAIN
        print('file--obj', domain_url, file_obj)
        accessory_dir = base_dir
        if not os.path.isdir(accessory_dir):
            os.mkdir(accessory_dir)
        if not str(file_obj.name).endswith(".ipa"):
            return result_json_err("只支持ipa文件和apk文件")
        order_id = time.strftime("%Y%m%d%H%M%S", time.localtime())
        upload_file = "%s/%s_%s" % (accessory_dir, order_id, file_obj.name)
        print(upload_file)
        with open(upload_file, 'wb') as new_file:
            for chunk in file_obj.chunks():
                new_file.write(chunk)

        if str(file_obj.name).endswith(".ipa"):
            app = parse_ipa(upload_file, domain_url, order_id)
            app.env = env
            AppInfo.objects.filter(name=app.name, env=env).delete()
            app.save()

            url = "%s/app/%s/%s" % (domain_url, app.env, app.identifier)
            img = qrcode.make(data=url)
            # 将二维码保存为图片
            app_icon = '%s/%s_%s_qr.png' % (base_dir, app.env, app.identifier)
            if os.path.exists(app_icon):
                os.remove(app_icon)
            with open(app_icon, 'wb') as f:
                img.save(f)
            # TODO 上传plist到https 路径下
            alert.send("有新鲜的iOS包出炉，请查收\n", url,
                       "名字：%s\n环境：%s\n包名：%s\n%s%s\n时间：%s\n" % (
                           app.name, app.env, app.identifier, msg, app.desc, app.datetime.strftime("%Y-%m-%d %H:%M")))

        # elif str(file_obj.name).endswith(".apk"):
        #     print()
        else:
            return result_json_err("不支持文件类型")

        return result_json_ok(app.identifier)
