# Using the third party `aiorun` instead of the `asyncio.run()` to avoid
# boilerplate.
import hl7
import os
from hl7.mllp import start_hl7_server
import argparse
import asyncio
from redis import Redis
from functools import partial
import psycopg2

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
        REDIS_CLIENT.rpush(queue_name,*values)
        
    except Exception as error:
        print(error)  
    
 
async def process_hl7_messages(hl7_reader, hl7_writer,channel_id):
    """This will be called every time a socket connects
    with us.
    """
    peername = hl7_writer.get_extra_info("peername")
    print(f"Connection established {peername}")
    try:
        # We're going to keep listening until the writer
        # is closed. Only writers have closed status.
        while not hl7_writer.is_closing():
            hl7_message = await hl7_reader.readmessage()
            # Now let's send the ACK and wait for the
            # writer to drain
            hl7_writer.writemessage(hl7_message.create_ack())
            await hl7_writer.drain()
            print(f'Received message\n {hl7_message}'.replace('\r', '\n'))
            push(channel_id,str(hl7_message))
    except Exception:
        # Oops, something went wrong, if the writer is not
        # closed or closing, close it.
        if not hl7_writer.is_closing():
            hl7_writer.close()
            await hl7_writer.wait_closed()
    print(f"Connection closed {peername}")


async def main(channel_id,port):
    try:
        # Start the server in a with clause to make sure we
        # close it
        process_hl7_messages_partial = partial(process_hl7_messages, channel_id=channel_id)
        async with await start_hl7_server(
            process_hl7_messages_partial, port=str(port)
        ) as hl7_server:
            # And now we server forever. Or until we are
            # cancelled...
            await  hl7_server.serve_forever()
    except Exception:
        print("Error occurred in main")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Integration engine!")

    # defining arguments for parser object
    parser.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "file_name", default = None,
                        help = "integration channel")
    
    parser.add_argument("-p", "--port", type = str, nargs = 1,
                        metavar = "port", default = None,
                        help = "Listner port")
                        
    # parse the arguments from standard input
    args = parser.parse_args()
    
    if args.channel != None:
    #set channel ID
        channel_id = args.channel[0]
        if args.port != None:
            port = args.port[0]
            # calling the main function
            asyncio.run(main(channel_id,port))