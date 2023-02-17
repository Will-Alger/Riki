#!/bin/bash

case ${1} in
    test)
        pytest --cov=wiki --cov-report html:cov_html --disable-warnings
        ;;
    debug)
        python3 Riki.py
        ;;
    *)
        exec "$@"
        ;;
    docs)
        pdoc3 --html --output-dir=/opt/app/wiki/web/static/docs --force wiki
        ;;
esac
