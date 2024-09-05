#!/usr/bin/env python3
"""An example HTTP server with GET and POST endpoints."""

import time
import argparse
import psycopg2
import json
from redis import Redis
from functools import partial
import os

redis_cli_eng = Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']), db=0)

def push(
    channel_id: str,
    *values
):
    try:
        json_channel = get_channle_json(channel_id)
        if "transformer" in json_channel['channel']['sourceConnector']:
            queue_name = "trans-" + channel_id
        else:
            queue_name = "dest-" + channel_id
        print(queue_name)
        redis_cli_eng.rpush(queue_name,*values)
        
    except Exception as error:
        print(error)  
        
def get_channle_json(
    id: str
):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host= os.environ['POSTGRES_HOST'],database=os.environ['POSTGRES_DB'],user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],port=int(os.environ['POSTGRES_PORT']))
        
        insert_sql = "select content from healthcare_channels where channel_id =%s;"
        cur = conn.cursor()
        cur.execute(insert_sql,(id,))
        json_channel = cur.fetchone()[0]
        cur.close()
        
        return json_channel
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
def run_reader():

    parser = argparse.ArgumentParser(description = "Integration engine!")

    # defining arguments for parser object
    parser.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "file_name", default = None,
                        help = "integration channel")
    
    parser.add_argument("-host", "--hostname", type = str, nargs = 1,
                        metavar = "hostname", default = None,
                        help = "IOStream hostname")
                        
    parser.add_argument("-p", "--iostreamport", type = str, nargs = 1,
                    metavar = "iostreamport", default = None,
                    help = "iostream port")
    
    parser.add_argument("-qname", "--qname", type = str, nargs = 1,
                metavar = "qname", default = None,
                help = "Queue Name")
                        
    # parse the arguments from standard input
    args = parser.parse_args()
    
    #set channel ID
    channel_id = args.channel[0]
    port = args.iostreamport[0]
    hostname = args.hostname[0]
    
    redis_cli = Redis(host=hostname, port=int(port), db=0)
    queue_name = args.qname[0]
    while True:
        msg = redis_cli.rpop(queue_name)
        if msg is None:
            time.sleep(0.1)
            continue
        try:
            push(channel_id,msg)
            print(f'data size in loop: {len((msg))}')
        except Exception as exc:
            print(f"Store failed")
            print(exc)
    

if __name__ == '__main__':
    run_reader()