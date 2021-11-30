#!/usr/bin/python
# -*- coding: UTF-8 -*-
from django.db import models
from django.utils import timezone


class AppInfo(models.Model):
    id = models.IntegerField(auto_created=True, primary_key=True)
    app = models.CharField(max_length=31, null=False)
    env = models.CharField(max_length=31, null=False)
    name = models.CharField(max_length=31, null=False)
    desc = models.CharField(max_length=127, null=False)
    download_url = models.CharField(max_length=255, null=False)
    display_image = models.CharField(max_length=255)
    identifier = models.CharField(max_length=63)  # ios
    datetime = models.DateTimeField(
        default=timezone.now
    )
