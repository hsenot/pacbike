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

# Getting all the departure events
sql = "select id as event_id from event where departure=true"
print sql
cur.execute(sql)
rows = cur.fetchall()

for row in rows:
	# Selecting the best candidate event for the arrival
	# Based on probability of arrival there and adequacy of trip time
	# The parameter k is given a value between 0 and 10
	# - closer to 10: dominant parameter is the delta duration (i.e. more stations represented in the output dataset)
	# - closer to 0: dominant parameter is the station's popularity (i.e. less stations represented in the output dataset)
	# Exploring the middle ground to make the repartition of arrival events (as recorded)
	# i.e: select station_id,count(*) from event where departure=false group by station_id order by count(*) desc
	# somewhat like the repartition of arrival events (as assigned based on spatio-temporal constraints)
	# i.e.: select d_station,count(*) from estimated_route group by d_station order by count(*) desc
	sql = """
		select * from
		(
		select event_origin, eoat, event_possible_dest, edat, probability_to_arrive_there/(5*abs(event_delta_duration-estimated_trip_duration)+1) as heuristic from
		(
		select e1.station_id event_origin,e1.at as eoat, e2.station_id as event_possible_dest, e2.at as edat, (SELECT EXTRACT(epoch FROM (e2.at-e1.at))/60) as event_delta_duration,
		(select avg_duration_mn from bike_route b where b.o_station=e1.station_id and b.d_station=e2.station_id) as estimated_trip_duration,
		cast((select count(id) from event e3 where e3.station_id=e2.station_id) as real)/cast((select count(id) from event e4 where departure=false) as real) as probability_to_arrive_there
		from event e1,event e2 where e1.id="""+str(row[0])+"""
		and e2.departure=false and e2.station_id <> e1.station_id and e2.at > e1.at and e2.at-e1.at < interval '2 hours'
		order by event_delta_duration
		) t 
		) s where heuristic is not null order by heuristic desc limit 1
	"""
	print sql
	cur.execute(sql)
	rows2 = cur.fetchall()

	# Persisting the result
	for row2 in rows2:
		sql = "INSERT INTO estimated_route (o_station,o_dt,d_station,d_dt,confidence) VALUES ("+str(row2[0])+",TIMESTAMP WITHOUT TIME ZONE '"+str(row2[1])+"',"+str(row2[2])+",TIMESTAMP WITHOUT TIME ZONE '"+str(row2[3])+"',"+str(row2[4])+")"
		print sql
		cur.execute(sql)
		conn.commit()
