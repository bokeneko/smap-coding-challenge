# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Sum
from django.http import HttpResponse
from django.utils import dateparse, timezone
from django.views.decorators.http import require_http_methods

from consumption.models import UserConsumption

import json


@require_http_methods(["GET"])
def summary(request):
    # check query
    q = request.GET.get(key="q", default=None)
    if q is not None:
        q = json.loads(q)
        user_ids = q.get("user_ids", None)
        if user_ids is not None:
            user_ids = [int(user_id) for user_id in user_ids]
    else:
        user_ids = None

    # select all with related data
    queryset = UserConsumption.objects.all().select_related()

    # filter user
    if user_ids is not None and len(user_ids) > 0:
        queryset = queryset.filter(user__user_id__in=user_ids)

    # group by date
    queryset = queryset\
                .extra(select={'date': 'date( datetime )'})\
                .values("user__user_id", "user__area__name", "user__tariff__name", "date")\
                .annotate(summary=Sum("value"))

    # create response data
    response_data = [{
        "user": {
                "id": v["user__user_id"],
                "area": v["user__area__name"],
                "tariff": v["user__tariff__name"],
            },
        "date": v["date"].strftime("%Y-%m-%d"),
        "summary": v["summary"]
        } for v in queryset]
    js = json.dumps(response_data, ensure_ascii=False)

    return HttpResponse(js, content_type='application/json')
