#!/usr/bin/env python3
"""An example HTTP server with GET and POST endpoints."""

import json
import time
import argparse
import psycopg2
import json
from redis import Redis
from functools import partial
import requests
import os
import http.client
from urllib.parse import urlparse
import ssl

REDIS_CLIENT = Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']), db=0)

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


def run_sender():

    parser = argparse.ArgumentParser(description = "Integration engine!")

    # defining arguments for parser object
    parser.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "file_name", default = None,
                        help = "integration channel")
    
    parser.add_argument("-u", "--url", type = str, nargs = 1,
                        metavar = "url", default = None,
                        help = "http/https url")
                        
    # parse the arguments from standard input
    args = parser.parse_args()
    
    #set channel ID
    channel_id = args.channel[0]
    url = args.url[0]
    queue_name = "dest-" + channel_id
    while True:
        msg = REDIS_CLIENT.rpop(queue_name)
        if msg is None:
            time.sleep(0.1)
            continue
        # Request association with remote
        print(f'data size in loop: {len((msg))}')
        try:
            print(msg)
            request_headers = {'Content-Type': 'application/json'}   
            posturl = urlparse(url)
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_cert_chain('/opt/certs/client-cert.pem','/opt/certs/client-key.pem')
            context.load_verify_locations('/opt/certs/ca-cert.pem')     
            conn = http.client.HTTPSConnection(posturl.hostname,posturl.port,context=context)
            print("connected")
            conn.request(method="POST", url=url, headers=request_headers, body=msg)
            response = conn.getresponse()
            print(response.status, response.reason)
        except Exception as exc:
            print(f"Store failed")
            print(exc)
    

if __name__ == '__main__':
    run_sender()