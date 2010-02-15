# -*- coding: utf-8 -*-

import time
from datetime import datetime

def timestamp ( timetuple = None ):
	if None == timetuple:
		return int( time.mktime( datetime.now().timetuple() ) )
	else:
		return int( time.mktime( timetuple ) )