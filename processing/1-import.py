import os,sys
import psycopg2
import json
from pprint import pprint

# Path to JSON files to import
fp = "../json/20140108"

# Database connection settings
db_name = "pacbike"
db_port = str(5432)
db_user = "bze"
db_password = "bze"

# Opening a database connection
try:
	conn_str = "dbname='"+db_name+"' user='"+db_user+"' password='"+db_password+"' host='localhost' port='"+db_port+"'"
	conn = psycopg2.connect(conn_str)
	if conn:
		print "Now connected to the database"
		# Keeping only the bare minimum table: gid and geom
except:
    print "I am unable to connect to the database"

cur = conn.cursor()

# Looping through all JSON files within the directory
for fn in os.listdir(fp):
	if fn.endswith(".jsonew"):

		# Reading the file into a string
		with open(fp+os.sep+fn) as myfile:
			json_data=myfile.read().replace('\n', '')

		# String replace for 2 un-wanted characters
		json_data=json_data.replace("\\x26","")
		json_data=json_data.replace("\\","")

		# Getting the file into a string
		data = json.loads(json_data)
		#pprint(data)

		# Extracting each top level JSON object and building a query with it
		# Each object looks like:
		# {u'id': u'55',
		#  u'installDate': u'1286866860000',
		#  u'installed': u'true',
		#  u'lastCommWithServer': u'1389270910518',
		#  u'lat': u'-37.831776',
		#  u'latestUpdateTime': u'1389252116855',
		#  u'locked': u'false',
		#  u'long': u'144.960818',
		#  u'name': u'Coventry St / Clarendon St',
		#  u'nbBikes': u'8',
		#  u'nbEmptyDocks': u'3',
		#  u'public': u'true',
		#  u'removalDate': {},
		#  u'temporary': u'false',
		#  u'terminalName': u'60050'}

		# Filename as a timestamp ready string
		fnt = fn[:4]+"-"+fn[4:6]+"-"+fn[6:8]+" "+fn[8:10]+":"+fn[10:12]+":"+fn[12:14]

		## Extraction of status for all stations
		for o in data:
			#print o["id"], o["nbBikes"], o["nbEmptyDocks"]
			sql = "INSERT INTO station_status (station_id,status_datetime,nb_bikes,nb_empty_docks) VALUES ("+o["id"]+",TIMESTAMP WITHOUT TIME ZONE '"+fnt+"',"+o["nbBikes"]+","+o["nbEmptyDocks"]+");"
			print sql
			cur.execute(sql)
			conn.commit()

		## Extraction of stations (should only be done once, kept for archival reasons)
		##for o in data:
		##	#print o["id"], o["nbBikes"], o["nbEmptyDocks"]
		##	sql = "INSERT INTO station (id,label,install_date,installed,locked,public,temporary,terminal_name,the_geom) VALUES ("+o["id"]+",'"+o["name"].replace("'","''")+"',null,"+o["installed"]+","+o["locked"]+","+o["public"]+","+o["temporary"]+",'"+o["terminalName"]+"',ST_SetSRID(ST_Point("+o["long"]+","+o["lat"]+"),4326));"
		##	print sql
		##	cur.execute(sql)
		##	conn.commit()
		##break

### Looping thru all lines from the batch route result (should only be done once, kept for archival reasons)
### with open('batchroute/out/B3.csv') as myroutefile:
###	for line in myroutefile:
###		# Extraction of the right parameters to build a SQL query
###		line_items = line.split(";")
###		if len(line_items) > 1:
###			if len(line_items[1]) > 1:
###				sql = "INSERT INTO bike_route (o_station,d_station,the_geom) VALUES ("+line_items[0].split("-")[0]+","+line_items[0].split("-")[1]+",ST_GeomFromText('LINESTRING("+line_items[1][:-1]+")',4326));"
###				print sql
###				cur.execute(sql)
###				conn.commit()		

### Assuming 2 minutes to get going / arrive and 15 km/h average speed (should only be done once, kept for archival reasons)
### sql = "UPDATE bike_route SET avg_duration_mn = round(ST_Length(ST_Transform(the_geom,3111))/(15000/60))+2"
###	print sql
###	cur.execute(sql)
###	conn.commit()

### Query to add the reverse routes (assumption: B->A use the same route as A->B)
### insert into bike_route (o_station,d_station,the_geom,avg_duration_mn)
### select d_station,o_station,ST_Reverse(the_geom) as the_geom,avg_duration_mn from bike_route