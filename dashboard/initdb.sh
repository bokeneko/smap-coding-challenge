#!/bin/bash

python /service/dashboard/manage.py makemigrations
python /service/dashboard/manage.py migrate
python /service/dashboard/manage.py import_data --datadir /service/data/
