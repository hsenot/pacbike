import os,sys,random
import psycopg2
import json
from pprint import pprint

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

# Getting all the stations
sql = "select id as station_id from station"
print sql
cur.execute(sql)
rows = cur.fetchall()

for row in rows:
	# Getting all the status for the station
	sql = "select nb_bikes,status_datetime from station_status where station_id="+str(row[0])+" order by status_datetime"
	print sql
	cur.execute(sql)
	rows2 = cur.fetchall()

	# 
	previous_nb_bike = -1
	for row2 in rows2:
		if (row2[0] <> previous_nb_bike):
			if previous_nb_bike == -1:
				previous_nb_bike = row2[0]
			else:
				diff = row2[0]-previous_nb_bike

				if diff <> 0:
					print "Difference:"+str(diff)
					if diff>0:
						# Arrival of a new bike
						departure = "false"
					else:
						# Departure bike
						departure = "true"

					# Emit as many events as the difference
					for x in range(0,abs(diff)):
						# Randomise the event time, as it seems the server is updated every 10 minutes or so
						rand_delay = random.randint(1, 10)

						sql = "INSERT INTO event (departure,station_id,at) VALUES ("+departure+","+str(row[0])+",TIMESTAMP WITHOUT TIME ZONE '"+str(row2[1])+"'- INTERVAL '"+str(rand_delay)+" minutes')"
						print sql
						cur.execute(sql)
						conn.commit()

					# Updating the previous nb of bikes to detect the next change
					previous_nb_bike = row2[0]
