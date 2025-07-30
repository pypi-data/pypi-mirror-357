
from . import stor2

import os.path

#was see some DCPlusPlus.xml creations but at older versions, now can't bring that back
#where? Nick(without this cannot connect nowhere),IncomingConnections(activ/pasiv this is also vital),Share(to share something, can be vital) TotalUpload(this is in confs)

a='''<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<DCPlusPlus>
	<Settings>
		<Nick type="string">'''
b='''</Nick>
		<ConfigVersion type="string">2.3.0</ConfigVersion>
		<Slots type="int">3</Slots>
		<TotalDownload type="int64">0</TotalDownload>
		<TotalUpload type="int64">0</TotalUpload>
	</Settings>
	<Share />
</DCPlusPlus>'''

def ini():
	f=stor2.get_file()
	if os.path.isfile(f)==False:
		from . import daem
		try:
			daem.dopen()
		except Exception:
			print("first daemon open error")
			return 0
		import time
		print("no daemon confs. sleep 5")
		time.sleep(5)
		if os.path.isfile(f):
			return -1
		print("cannot open "+f)
		daem.dclose() #this is sync

		import xml.etree.ElementTree as ET
		from . import nick
		s=a+nick.name.get_text()+b
		e=ET.fromstring(s)
		t = ET.ElementTree(element=e)
		t.write(f)
	return 1
