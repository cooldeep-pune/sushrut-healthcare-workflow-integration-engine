import os
import argparse
import psycopg2
import json
from functools import partial
from pydicom import dcmread, dcmwrite
from pydicom.filebase import DicomFileLike
from redis import Redis
from io import BytesIO
import time
from pydicom.errors import InvalidDicomError
__version__ = "0.3.0"

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
    queue_name = "dest-" + channel_id
    print(queue_name)
    REDIS_CLIENT.rpush(queue_name,*values)
    
def push_to_queue(
    channel_id: str,
    ds: dict
) -> None:

    with BytesIO() as buffer:
        # create a DicomFileLike object that has some properties of DataSet
        memory_dataset = DicomFileLike(buffer)
        # write the dataset to the DicomFileLike object
        dcmwrite(memory_dataset, ds)
        
        memory_dataset.seek(0)

        push(channel_id,memory_dataset.read())

    
    

def anonymizer(
    channel_id: str,
    ds
) -> None:
    ds.PatientName='XXXX^XXXXXX'
    ds.PatientID='111.XXXXXXX'
    push_to_queue(channel_id,ds)


def main():

    parser = argparse.ArgumentParser(description = "Integration engine!")

    # defining arguments for parser object
    parser.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "file_name", default = None,
                        help = "integration channel")
    
    # parse the arguments from standard input
    args = parser.parse_args()
     
    # calling functions depending on type of argument
    queue_name = "trans-" + args.channel[0]
    print(queue_name)

    while True:
        msg = REDIS_CLIENT.rpop(queue_name)
        if msg is None:
            time.sleep(0.1)
            continue
        print(f'data size in loop: {len((msg))}')
        print(f"Sending file")
        try:
            ds = dcmread(BytesIO(msg),force=True)
            anonymizer(args.channel[0],ds)
        except InvalidDicomError:
            print(f"Bad DICOM file")
        except Exception as exc:
            print(f"Store failed")
            print(exc)
        
if __name__ == "__main__":
    # calling the main function
    main()