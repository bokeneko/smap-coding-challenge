# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.


def summary(request):
    context = {}
    return render(request, 'consumption/summary.html', context)


def detail(request, user_id):
    context = {
        "user_id": int(user_id)
    }
    return render(request, 'consumption/summary.html', context)
