#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.http import JsonResponse


def result_json_err(code, msg):
    return JsonResponse({"code": code, "message": msg})
    pass


def bad_request(request):
    return result_json_err(400, '400')


def permission_denied(request):
    return result_json_err(400, '403')


def page_not_found(request):
    return result_json_err(400, '404')


def server_error(request):
    return result_json_err(400, '500')
