# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.test import TestCase, Client
from django.utils import dateparse, timezone

from consumption.management.commands.import_data import import_user, import_consumption

import csv
import json
import os
import os.path
import random
import time
import urllib


random.seed(time.time())


class ApiTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.datadir = os.environ.get('DATADIR')
        user_data_file_path = os.path.join(self.datadir, "user_data.csv")
        consumption_data_dir_path = os.path.join(self.datadir, "consumption")

        # import test data to db
        import_user(user_data_file_path)
        import_consumption(consumption_data_dir_path)

        # load user data
        with open(user_data_file_path) as f:
            reader = csv.reader(f)
            next(reader)
            self.users = [d for d in reader]

        # load consumption data
        current_tz = timezone.get_current_timezone()
        self.consumption_data = {}
        dup_check = set()
        for user in self.users:
            user_id = int(user[0])
            with open(os.path.join(consumption_data_dir_path, "{}.csv".format(user_id))) as f:
                reader = csv.reader(f)
                next(reader)
                for d in reader:
                    dup_key = (user_id, d[0])
                    if dup_key in dup_check:
                        continue
                    dup_check.add(dup_key)
                    date = current_tz.localize(dateparse.parse_datetime(d[0])).strftime("%Y-%m-%d")
                    key = (user_id, date)
                    if key not in self.consumption_data:
                        self.consumption_data[key] = 0
                    self.consumption_data[key] += float(d[1])

    def test_summary(self):
        # call api
        r = self.client.get("/api/v1/summary/")
        # check
        keys = set(self.consumption_data.keys())
        for r in r.json():
            key = (r["user"]["id"], r["date"])
            original = self.consumption_data.get(key, None)
            self.assertIsNotNone(original)
            self.assertEqual(original, r["summary"])
            keys.remove(key)
        self.assertEqual(0, len(keys))

    def test_user_summary(self):
        user = random.choice(self.users)
        user_id = int(user[0])
        # call api
        q = {
            "q": json.dumps({
                "user_ids": [user_id]
            }),
        }
        r = self.client.get("/api/v1/summary/?{}".format(urllib.urlencode(q)))
        user_rsp = r.json()
        # num check
        keys = set([key for key in self.consumption_data.keys() if key[0] == user_id])
        for r in r.json():
            key = (r["user"]["id"], r["date"])
            original = self.consumption_data.get(key, None)
            self.assertIsNotNone(original)
            self.assertEqual(original, r["summary"])
            keys.remove(key)
        self.assertEqual(0, len(keys))
