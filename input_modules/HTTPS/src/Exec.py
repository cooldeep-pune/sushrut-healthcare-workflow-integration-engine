import os
import argparse
import psycopg2
import json

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
            

def run_connector(
    channel_id: str,
    json_channel: dict
) -> None:

    """ staring input connector """
    sourceDockerContainer = json_channel['channel']['sourceConnector']['properties']['@class']
    sourceDockerContainerName = sourceDockerContainer.replace('/','-')
    
    print('Starting source connector '+sourceDockerContainerName)
    
    src_port = json_channel['channel']['sourceConnector']['properties']['listenerConnectorProperties']['port']
    
    os.system("python3 -u /opt/healthcare-workflow/httpsReceiver.py -p " + src_port + " -c " + channel_id)
    
    
    

def run(
    args: str
) -> None:
    json_channel = get_channle_json(args.channel[0])
    channel_id = args.channel[0]
    run_connector(channel_id,json_channel)


def main():

    parser = argparse.ArgumentParser(description = "Integration engine!")

    # defining arguments for parser object
    parser.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "file_name", default = None,
                        help = "integration channel")
    
    # parse the arguments from standard input
    args = parser.parse_args()
     
    # calling functions depending on type of argument
    if args.channel != None:
        run(args)
        
if __name__ == "__main__":
    # calling the main function
    main()