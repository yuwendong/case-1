# -*- coding: utf-8 -*-

import os
from config import DYNAMIC_XAPIAN_WEIBO_STUB_PATH
from xapian_weibo.xapian_backend import XapianSearch

path = DYNAMIC_XAPIAN_WEIBO_STUB_PATH

def getXapianWeiboByDate(datestr):
    # datestr: 20130908    
    stub_file = path + datestr

    if os.path.exists(stub_file):
        xapian_search_weibo = XapianSearch(stub=stub_file, schema_version=5)
    	return xapian_search_weibo
    else:
    	return None


def getXapianWeiboByDuration(datestr_list):
    stub_file_list = []

    for datestr in datestr_list:
        stub_file = path + datestr

	if os.path.exists(stub_file):
	    stub_file_list.append(stub_file)

    if len(stub_file_list):
        xapian_search_weibo = XapianSearch(stub=stub_file_list, include_remote=True, schema_version=5)
        return xapian_search_weibo

    else:
    	return None
