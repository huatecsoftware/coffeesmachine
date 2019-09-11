# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class modOrder(models.Model):
    Taste = models.CharField(max_length=200, verbose_name='口味')
    Stime = models.DateTimeField(verbose_name='接单时间')
    Etime = models.DateTimeField(
        max_length=200, verbose_name='订单完成时间')
    Uname = models.CharField(max_length=200, verbose_name='用户名')
    Gender = models.CharField(max_length=200, verbose_name='性别')
    Phone = models.CharField(max_length=200, verbose_name='电话')
    Status = models.CharField(max_length=200, verbose_name='订单状态')
    Number = models.CharField(max_length=200, verbose_name='订单号')
    Pos = models.IntegerField(verbose_name='仓位号', default=0)

    def __str__(self):
        return self.Taste

    class Meta:
        verbose_name = '订单表'


class User(models.Model):
    name = models.CharField(max_length=10, verbose_name='姓名')
    gender = models.CharField(max_length=2, verbose_name='性别')
    phone = models.CharField(max_length=11, verbose_name='手机号')
    picture = models.CharField(max_length=100, verbose_name='照片')

    def __str__(self):
        return self.name+self.phone

    class Meta:
        verbose_name = '用户表'


class modClear(models.Model):
    time = models.DateTimeField(max_length=200, verbose_name='清理日期')

    def __str__(self):
        return str(self.time)

    class Meta:
        verbose_name = '清理表'
