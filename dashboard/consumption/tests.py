# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.test import TestCase
from django.utils import dateparse, timezone

from consumption.models import Area, Tariff, User, UserConsumption
from consumption.management.commands.import_data import import_user, import_consumption

import csv
import os
import os.path
import random
import time


random.seed(time.time())


class UserConsumptionTestCase(TestCase):
    def setUp(self):
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
        self.consumption_data = {}
        for user in self.users:
            user_id = int(user[0])
            with open(os.path.join(consumption_data_dir_path, "{}.csv".format(user_id))) as f:
                reader = csv.reader(f)
                next(reader)
                for d in reader:
                    key = (user_id, d[0].strip())
                    if key in self.consumption_data:
                        continue
                    self.consumption_data[key] = float(d[1])

    def test_user_attribute(self):
        user = random.choice(self.users)
        user_id = int(user[0])
        # user exist
        user_elem = None
        try:
            user_elem = User.objects.get(user_id=user_id)
        except:
            pass
        self.assertIsNotNone(user_elem)
        # user area is equal
        self.assertEqual(user_elem.area.name, user[1])
        # user tariff is equal
        self.assertEqual(user_elem.tariff.name, user[2])

    def test_consumption(self):
        keys = set(self.consumption_data.keys())
        consumptions = UserConsumption.objects.all().select_related()
        for consumption in consumptions:
            key = (consumption.user.user_id, consumption.datetime.strftime("%Y-%m-%d %H:%M:%S"))
            original = self.consumption_data.get(key, None)
            self.assertIsNotNone(original)
            self.assertEqual(original, consumption.value)
            keys.remove(key)
        self.assertEqual(0, len(keys))
