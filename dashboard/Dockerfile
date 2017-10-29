FROM python:2.7
RUN apt-get -y update
RUN apt-get -y upgrade

# setup nginx
RUN apt-get install -y build-essential nginx
ADD etc/nginx/nginx.conf.template /etc/nginx/nginx.conf

# setup django
ENV PYTHONUNBUFFERED 1
RUN mkdir -p /service/dashboard
WORKDIR /service/dashboard
ADD requirements.txt /service/
RUN pip install -r /service/requirements.txt
ADD dashboard /service/dashboard/dashboard/
ADD api /service/dashboard/api/
ADD consumption/ /service/dashboard/consumption/
ADD manage.py /service/dashboard/
ADD uwsgi.ini /service/dashboard/
RUN mkdir -p /service/dashboard/static
RUN /service/dashboard/manage.py collectstatic --noinput
ADD entrypoint.sh /service/
ADD initdb.sh /service/
ADD tests.sh /service/
RUN mkdir -p /service/data
