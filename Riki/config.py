# encoding: utf-8
import os
SECRET_KEY=os.environ.get("SECRET_KEY")
TITLE=os.environ.get("TITLE")
HISTORY_SHOW_MAX=os.environ.get("HISTORY_SHOW_MAX")
PIC_BASE = os.environ.get("PIC_BASE")
CONTENT_DIR = os.environ.get("CONTENT_DIR")
USER_DIR = os.environ.get("USER_DIR")
NUMBER_OF_HISTORY = os.environ.get("NUMBER_OF_HISTORY")
PRIVATE = os.environ.get("PRIVATE")
#PRIVATE = False