#!/bin/bash

service nginx start
uwsgi --ini /service/dashboard/uwsgi.ini
