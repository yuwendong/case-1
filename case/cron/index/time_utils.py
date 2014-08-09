# -*-coding: utf-8 -*

import time
import datetime


def ts2datetime_full(ts):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ts))



