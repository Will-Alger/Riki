#!/bin/bash


# remove volume and rebuild to update existing database.

case ${1} in
    test)
        pytest --cov=wiki --cov-report html:cov_html --disable-warnings
        ;;
    debug)
        python3 /opt/app/wiki/web/init_db.py
        python3 Riki.py
        ;;
    docs)
        pdoc3 --html --output-dir=/opt/app/wiki/web/static/docs --force wiki
        ;;
    *)
        exec "$@"
        ;;
esac
