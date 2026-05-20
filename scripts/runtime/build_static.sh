#!/usr/bin/env bash

export $(egrep -v '^#' ./.test.env | xargs)

export DB_CONNECTION='{"dbname":"postgres","username":"postgres","password":"postgres","host":"db","port":5432}'

python manage.py collectstatic --no-input
