#!/bin/bash

python /service/dashboard/manage.py makemigrations
python /service/dashboard/manage.py test
