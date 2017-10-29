from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import dateparse, timezone

from consumption.models import Area, Tariff, User, UserConsumption

from multiprocessing import Pool

import csv
import os
import os.path
import re


CONSUMPTION_FILE_PATH = re.compile(r"([0-9]+)\.csv")


def _read_consumption_file(args):
    user_id, file_path, current_tz = args
    consumptions = []
    with open(file_path, "rb") as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            native_datetime = dateparse.parse_datetime(row["datetime"])
            localize_datetime = current_tz.localize(native_datetime)
            consumptions.append((localize_datetime, float(row["consumption"])))
    return (user_id, consumptions)


def import_consumption(consumption_data_dir, worker_num=10):
    # read data
    current_tz = timezone.get_current_timezone()
    files = os.listdir(consumption_data_dir)
    data_files = []
    for file_path in files:
        m = CONSUMPTION_FILE_PATH.match(file_path)
        if m is None:
            continue
        user_id = int(m.groups()[0])
        data_files.append((
                    user_id,
                    os.path.join(consumption_data_dir, file_path),
                    current_tz))
    p = Pool(worker_num)
    all_user_data = p.map(_read_consumption_file, data_files)

    # cache user
    user_cache = {}
    users = User.objects.all()
    for user in users:
        user_cache[user.user_id] = user

    # process data
    consumptions = {}
    for user_id, user_consumptions in all_user_data:
        if user_id not in user_cache:
            continue
        user = user_cache[user_id]
        for datetime, value in user_consumptions:
            consumption = UserConsumption(
                user=user,
                datetime=datetime,
                value=value)
            # TODO Handle duplicated data
            # For this time, I will just skip it.
            key = (user, datetime)
            if key in consumptions:
                continue
            consumptions[key] = consumption

    # TODO Handle dupulicated data already exist in DB
    # This time, I just insert it. So, If dupulicated data exists, exception will occor.
    UserConsumption.objects.bulk_create(consumptions.values())


def import_user(user_data_file_path):
    area_cache = {}
    tariff_cache = {}

    # cache area
    areas = Area.objects.all()
    for area in areas:
        area_cache[area.name] = area
    # cache tariff
    tariffs = Tariff.objects.all()
    for tariff in tariffs:
        tariff_cache[tariff.name] = tariff

    # process user data file
    users = {}
    with open(user_data_file_path, "rb") as f:
        reader = csv.DictReader(f, delimiter=',')
        for row in reader:
            if row["area"] not in area_cache:
                area, _ = Area.objects.get_or_create(
                            name=row["area"])
                area_cache[row["area"]] = area
            if row["tariff"] not in tariff_cache:
                tariff, _ = Tariff.objects.get_or_create(
                            name=row["tariff"])
                tariff_cache[row["tariff"]] = tariff
            user_id=int(row["id"])
            # TODO Handle duplicated user
            # For this time, I will just skip it.
            if user_id in users:
                continue
            user = User(
                user_id=user_id,
                area=area_cache[row["area"]],
                tariff=tariff_cache[row["tariff"]])
            users[user_id] = user

    # TODO Handle dupulicated users already exist in DB
    # This time, I just insert it. So, If dupulicated user exists, exception will occor.
    User.objects.bulk_create(users.values())


class Command(BaseCommand):
    help = 'import data'

    def add_arguments(self, parser):
        parser.add_argument(
            "--datadir",
            dest="datadir",
            required=True,
            help="data dir file path")
        parser.add_argument(
            "--workernum",
            action="store_const",
            dest="workernum",
            const=10,
            help="number of workers to process consumption data")

    def handle(self, *args, **options):
        with transaction.atomic():
            print "Start importing data. This will take while..."
            user_data_file_path = os.path.join(options["datadir"], "user_data.csv")
            consumption_data_dir_path = os.path.join(options["datadir"], "consumption")
            import_user(user_data_file_path)
            import_consumption(consumption_data_dir_path, worker_num=options["workernum"])
            print "Finished!"
