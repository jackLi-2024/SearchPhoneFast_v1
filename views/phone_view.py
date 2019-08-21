#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json
import time
import logging
import requests

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

from rest_framework.views import APIView
from resource.common import output
from resource.common.util import DictToObj
from resource.extension.log import logging
from resource.common.catch_exception import catch_exception
from django.shortcuts import render
from itertools import product

ES_HOST = "192.168.1.2"
ES_PORT = "9200"


class IndexView(APIView):
    @catch_exception
    def get(self, request, *args, **kwargs):
        return render(request, "index.html")

    @catch_exception
    def post(self, request, *args, **kwargs):
        data = self.request.data
        phone = data.get("phone")
        phone_ = phone
        city = data.get("city")
        error = ""
        if len(phone) != 11:
            error = "手机号格式错误，必须是11位"
        try:
            int(phone[:3])
        except:
            error = "电话号码前三位必须是数字"

        try:
            int(phone[-4:])
        except:
            error = "电话号码后四位必须是数字"
        try:
            if phone[0] != str(1):
                error = "电话号码格式错误，首位必须为1"
        except:
            error = "号码不能为空"

        if error:
            return render(request, "index.html", {"error": error})

        mid_data = phone[3:7]
        result = self.filter_condition(mid_data)
        data = []
        for one in result:
            data.append({"_id": phone[:3] + one + phone[7:]})
        es_url = "http://" + ES_HOST + ":" + ES_PORT + "/phone/_mget"
        body = {
            "docs": data
        }
        print(json.dumps(body))
        try:
            response = requests.get(es_url, json=body).json()["docs"]
        except Exception as e:
            logging.exception(str(e))
            error = "请求异常，请联系管理员"
            response = []

        data_list = []
        index = 0
        for one in response:
            try:
                if one.get("found"):
                    cityName = one.get("_source").get("city")
                    province = one.get("_source").get("province")
                    phone = one.get("_source").get("phone")
                else:
                    continue
            except:
                continue

            if cityName == city or not city or city in province:
                index += 1
                data_list.append({"phone": phone, "city": cityName, "province": province, "index": index})

        if not data_list and not error:
            error = "没有相关数据"

        return render(request, "index.html", {"data": data_list, "error": error, "city": city, "phone": phone_})

    def filter_condition(self, mid_data="0**2"):
        length = len(mid_data)
        if not length:
            return set()
        l = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        data = product(l, repeat=length)
        result = set()
        filter_c = {}
        for i in range(len(mid_data)):
            if mid_data[i] != "*":
                filter_c[i] = mid_data[i]
        for one in data:
            a = list(one)
            for i in filter_c:
                a[i] = filter_c[i]
            a = "".join(a)
            result.add(a)
        return result
