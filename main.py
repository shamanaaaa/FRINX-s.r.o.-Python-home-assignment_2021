import psycopg2
import json

# opening JSON file
f = open('configClear_v2.json')
data = json.load(f)
f.close()
 
# filter target data
interface_data = (data["frinx-uniconfig-topology:configuration"]["Cisco-IOS-XE-native:native"]["interface"])

# creating list of choosen interfaces for future updates
choosen_interfaces = ["Port-channel", "TenGigabitEthernet", "GigabitEthernet"]

# Establishing DB connection
conn = psycopg2.connect(database="cisco", user='postgres', password='admin', host='127.0.0.1', port= '5432')
conn.autocommit = True
cursor = conn.cursor()

# Creating table if not exist
try:
    create_table ='''CREATE TABLE INTERFACES(
        id SERIAL PRIMARY KEY,
    	name VARCHAR(255) NOT NULL,
    	description VARCHAR(255),
    	config json,
    	port_channel_id INTEGER,
    	max_frame_size INTEGER
    )'''
    cursor.execute(create_table)
    print("Table created successfully........")
    conn.commit()
except psycopg2.Error as e:
    print(e)

# loop for selected interfaces and write line by line to DB
for group in choosen_interfaces:
    for interface in interface_data[group]:
        name = (f'{group}{interface["name"]}')
        try:
            description = (interface["description"])
        except KeyError:
            description = None
        config = json.dumps(interface) 
        try:
            port_channel_id = interface["Cisco-IOS-XE-ethernet:channel-group"]["number"]
        except KeyError:
            port_channel_id = "NULL"
        try:
            max_frame_size = interface["mtu"]
        except KeyError:
            max_frame_size = "NULL"
   
        cursor.execute(f'''INSERT INTO INTERFACES(name, description, config, port_channel_id, max_frame_size)
        VALUES('{name}', '{description}', '{config}', {port_channel_id}, {max_frame_size})''')
        print(f"Writing row for interface {name}")

conn.commit()
conn.close()