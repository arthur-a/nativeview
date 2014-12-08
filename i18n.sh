#!/bin/bash

PROJECT="nativeview"
POT_FILE=$PROJECT/locale/$PROJECT.pot

case $1 in
    update)
        xgettext -d $PROJECT -o $POT_FILE $PROJECT/*.py
        msgmerge --update $PROJECT/locale/ru/LC_MESSAGES/$PROJECT.po $POT_FILE
        ;;
    compile)
        msgfmt $PROJECT/locale/ru/LC_MESSAGES/$PROJECT.po -o $PROJECT/locale/ru/LC_MESSAGES/$PROJECT.mo
        ;;
esac
