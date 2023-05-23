#!/bin/sh

python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py demodata

case "$RTE" in
    dev )
        echo "***** Development mode."
        coverage run --source="." --omit=manage.py manage.py test --verbosity 2
        coverage report -m
        python manage.py runserver 0.0.0.0:8000
        ;;
    test )
        echo "***** Test mode."
        coverage run --source="." --omit=manage.py manage.py test --verbosity 2
        coverage report -m --fail-under=80
        ;;
    prod )
        echo "***** Production mode."
        python manage.py check --deploy
esac