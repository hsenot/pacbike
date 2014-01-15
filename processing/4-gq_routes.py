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
sql = "select id,o_dt as start,round((SELECT EXTRACT(epoch FROM (d_dt-o_dt))/60)) as duration from estimated_route order by start"
print sql
cur.execute(sql)
rows = cur.fetchall()

all_events = {}
event_ct = 0

for row in rows:
	# Getting the list of cells that this route intersects
	# Each route will be an object in the output JSON
	sql = """
		select string_agg(cell,',') as cell_list from
		(
		select c_x||'X'||c_y as cell from
		(
		select c.x as c_x,c.y as c_y,t.the_geom as route_geom, c.the_geom as cell_geom, ST_Intersection(t.the_geom,c.the_geom) as inter from
		(
		select a.o_station,a.d_station,ST_SetSRID(the_geom,4326) as the_geom
		from estimated_route a, bike_route b
		where a.id="""+str(row[0])+""" and a.o_station=b.o_station and a.d_station=b.d_station
		) t, cbd_cell c
		where ST_Intersects(t.the_geom,c.the_geom)
		) s
		order by least(ST_Line_Locate_Point(route_geom,ST_StartPoint(inter)),
		ST_Line_Locate_Point(route_geom,ST_EndPoint(inter)))
		) u
	"""
	#print sql
	cur.execute(sql)
	rows2 = cur.fetchall()

	# Exploring the result (if any, as routes may not intersect with CBD cells)
	for row2 in rows2:
		if row2[0] <> None:
			# Putting the resulting object into a JSON format
			current_event_route = {}
			current_event_route["s"] = str(row[1])
			current_event_route["d"] = str(row[2])
			current_event_route["l"] = str(row2[0])

			# Putting this object into the larger dictionary of routed events
			all_events[event_ct] = current_event_route
			event_ct += 1

# When all routed events added to the dictionary, we export it as JSON
json_str = json.dumps(all_events, sort_keys=True, indent=4, separators=(',', ': '))

with open('../routed_events/assets.json', "w") as f:
	f.write(json_str)