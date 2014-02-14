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
sql = "select e.id,e.o_dt as start,(select round((SELECT EXTRACT(epoch FROM (e.o_dt-er.o_dt))/60)) from estimated_route er order by er.o_dt limit 1) as mn_since_first,round((SELECT EXTRACT(epoch FROM (e.d_dt-e.o_dt))/60)) as duration from estimated_route e order by start"
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
			current_event_route["d"] = str(int(row[3]))
			current_event_route["l"] = str(row2[0])
			current_event_route["o"] = str(int(row[2]))

			# Testing if all steps of the route correspond to either:
			# - an horizontal move
			# - a vertical move
			# Flags the routes that do not!
			first = True
			continuousFlag = True
			previousStp = ""
			for stp in current_event_route["l"].split(","):
				if first:
					previousStp = stp
					first = False
					continue
				else:
					#print "stp:"+stp
					(x1,y1) = stp.split("X")
					(x2,y2) = previousStp.split("X")

					if abs(int(x1)-int(x2))+abs(int(y1)-int(y2))>1:
						print "The route "+str(row[0])+" seem to be discontinuous between "+x1+"X"+y1+" and "+x2+"X"+y2+". Not exporting it to JSON."
						continuousFlag = False
						break
					else:
						pass
					previousStp = stp

			if continuousFlag:
				# The route is continuous, putting the object into the larger dictionary of routed events
				all_events[event_ct] = current_event_route
				event_ct += 1



# When all routed events added to the dictionary, we export it as JSON
json_str = json.dumps(all_events, sort_keys=True, indent=4, separators=(',', ': '))

with open('../routed_events/assets.json', "w") as f:
	f.write(json_str)
