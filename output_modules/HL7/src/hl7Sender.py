#!/usr/bin/env python3
"""An example HTTP server with GET and POST endpoints."""

import time
import argparse
import psycopg2
import json
from redis import Redis
from functools import partial
import os

import hl7
from hl7.mllp import open_hl7_connection
import asyncio

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
            
async def sendhl7(message,remotehost,remoteport):

    # Open the connection to the HL7 receiver.
    # Using wait_for is optional, but recommended so
    # a dead receiver won't block you for long
    hl7_reader, hl7_writer = await asyncio.wait_for(
        open_hl7_connection(remotehost, remoteport),
        timeout=10,
    )

    hl7_message = hl7.parse(message)

    # Write the HL7 message, and then wait for the writer
    # to drain to actually send the message
    hl7_writer.writemessage(hl7_message)
    await hl7_writer.drain()
    print(f'Sent message\n {hl7_message}'.replace('\r', '\n'))

    # Now wait for the ACK message from the receiever
    hl7_ack = await asyncio.wait_for(
      hl7_reader.readmessage(),
      timeout=10
    )
    print(f'Received ACK\n {hl7_ack}'.replace('\r', '\n'))

def run_sender():

    parser = argparse.ArgumentParser(description = "Integration engine!")

    # defining arguments for parser object
    parser.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "file_name", default = None,
                        help = "integration channel")
    
    parser.add_argument("-rport", "--remoteport", type = str, nargs = 1,
                        metavar = "remoteport", default = None,
                        help = "hl7 server remoteport")
                        
    parser.add_argument("-raddr", "--remotehost", type = str, nargs = 1,
                    metavar = "remotehost", default = None,
                    help = "hl7 server remotehost")
                        
    # parse the arguments from standard input
    args = parser.parse_args()
    
    #set channel ID
    channel_id = args.channel[0]
    port = args.remoteport[0]
    remotehost = args.remotehost[0]
    
    queue_name = "dest-" + channel_id
    while True:
        msg = REDIS_CLIENT.rpop(queue_name)
        if msg is None:
            time.sleep(0.1)
            continue
        # Request association with remote
        print(f'data size in loop: {len((msg))}')
        try:
            hl7_payload = msg
            asyncio.run(sendhl7(hl7_payload,remotehost,int(port)))
        except Exception as exc:
            print(f"Store failed")
            print(exc)
    

if __name__ == '__main__':
    run_sender()