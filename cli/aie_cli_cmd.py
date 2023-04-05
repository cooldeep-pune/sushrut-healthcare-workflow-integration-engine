import os
import argparse
import psycopg2
import json
import socket
     
import xml2json

def insert_or_update_channel(
    id: str,
    channel_name: str,
    string_channel: str
):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host= os.environ['POSTGRES_HOST'],database=os.environ['POSTGRES_DB'],user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],port=int(os.environ['POSTGRES_PORT']))
        
        update_sql = "UPDATE healthcare_channels SET content=%s, channel_name=%s WHERE channel_id=%s;"
        # create a cursor
        cur_update = conn.cursor()
        cur_update.execute(update_sql,(string_channel,channel_name,id,))
        #print(cur_update.query)
        cur_update.close()
        conn.commit()
        
        insert_sql = "INSERT INTO healthcare_channels(channel_id,channel_name,content) values(%s,%s,%s);"
        cur_insert = conn.cursor()
        cur_insert.execute(insert_sql,(id,channel_name,string_channel,))
        #print(cur_insert.query)
        cur_insert.close()
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

def deploy_channel(
    id: str
):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host= os.environ['POSTGRES_HOST'],database=os.environ['POSTGRES_DB'],user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],port=int(os.environ['POSTGRES_PORT']))
               
        insert_sql = "INSERT INTO channels_deployed(deployed_channel_id) values(%s);"
        cur_insert = conn.cursor()
        cur_insert.execute(insert_sql,(id,))
        #print(cur_insert.query)
        cur_insert.close()
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
            
def undeploy_channel(
    id: str
):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host= os.environ['POSTGRES_HOST'],database=os.environ['POSTGRES_DB'],user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],port=int(os.environ['POSTGRES_PORT']))
               
        delete_sql = "DELETE FROM channels_deployed where deployed_channel_id = %s;"
        cur_delete = conn.cursor()
        cur_delete.execute(delete_sql,(id,))
        #print(cur_insert.query)
        cur_delete.close()
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
def delete_channel_db(
    id: str
):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host= os.environ['POSTGRES_HOST'],database=os.environ['POSTGRES_DB'],user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],port=int(os.environ['POSTGRES_PORT']))
               
        delete_sql = "DELETE FROM healthcare_channels where channel_id = %s;"
        cur_delete = conn.cursor()
        cur_delete.execute(delete_sql,(id,))
        #print(cur_insert.query)
        cur_delete.close()
        conn.commit()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')

            
def load_channel(
    name: str
):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host= os.environ['POSTGRES_HOST'],database=os.environ['POSTGRES_DB'],user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],port=int(os.environ['POSTGRES_PORT']))
        
        select_sql = "select content from healthcare_channels WHERE channel_name=%s;"
        # create a cursor
        cur_select = conn.cursor()
        cur_select.execute(select_sql,(name,))
        result = cur_select.fetchone()[0]
        cur_select.close()
        
        return result
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
def readFile(
    file_name: str
) -> None:

    data =""
    
    with open(file_name, 'r') as f:
        data = f.read().rstrip()
    
    return data

def trigger_command(
    command: str
) -> None:
    try:

        och_host = os.environ['ORCHESTRATOR_HOST']
        och_port = os.environ['ORCHESTRATOR_PORT']
        print(och_host)
        print(och_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        sock.connect((och_host, int(och_port))) 
        sock.send(command.encode("utf-8"))  
        print(sock.recv(1024))
        sock.close()
    
    except Exception as error:
        print('Error in connection'+ error)
        
def undeploy(
    args: str
) -> None:

    json_channel = load_channel(args.undeploy[0])
    
    if json_channel is  None:
        print('Channel does not exist in System ' + args.undeploy[0])
        return;
        
    channel_id = json_channel['channel']['id']
    print(channel_id)
    undeploy_channel(channel_id)
    
    # trigger run to orchestrator
    command = "stop " + channel_id
    trigger_command(command)
    

def deploy(
    args: str
) -> None:
    
    json_channel = load_channel(args.deploy[0])
    if json_channel is  None:
        print('Channel does not exist in System ' + args.deploy[0])
        return;
    channel_id = json_channel['channel']['id']
    
    deploy_channel(channel_id)
    # trigger run to orchestrator
    command = "run " + channel_id
    print(command)
    trigger_command(command)


def import_xml_channel(args):

    string_channel = xml2json.xml2json(readFile(args.import_xml_channel[0]))
    json_channel = json.loads(string_channel)
    channel_id = json_channel['channel']['id']
    channel_name = json_channel['channel']['name']
    insert_or_update_channel(channel_id,channel_name,string_channel)
    
def export_xml_channel(args):
    json_channel = load_channel(args.export_xml_channel[0])
    string_channel = xml2json.json2xml(json.dumps(json_channel))
    
    with open(args.export_xml_channel[1], "w") as xml_file:
        xml_file.write(string_channel)
    
def import_json_channel(args):

    string_channel = readFile(args.import_json_channel[0])
    json_channel = json.loads(string_channel)
    channel_id = json_channel['channel']['id']
    channel_name = json_channel['channel']['name']
    insert_or_update_channel(channel_id,channel_name,string_channel)

def export_json_channel(args):
    json_channel = load_channel(args.export_json_channel[0])
    
    with open(args.export_json_channel[1], "w") as json_file:
        json_file.write(json.dumps(json_channel))

def delete_channel(args):
    json_channel = load_channel(args.delete_channel[0])
    channel_id = json_channel['channel']['id']
    delete_channel_db(channel_id)
    
def main():

    parser = argparse.ArgumentParser(description = "A cli for integration engine!")

    # defining arguments for parser object
    parser.add_argument("-d", "--deploy", type = str, nargs = 1,
                        metavar = "file_name", default = None,
                        help = "Deploys integration channel")
    
    parser.add_argument("-ud", "--undeploy", type = str, nargs = 1,
                        metavar = "undeploy", default = None,
                        help = "Undeploys integration channel")

    # parse the arguments from standard input
   
    
    parser.add_argument("-ix", "--import_xml_channel", type = str, nargs = 1,
                    metavar = "import_xml_channel", default = None,
                    help = "Imports XML integration channel")
    
    parser.add_argument("-ex", "--export_xml_channel", type = str, nargs = 2,
                metavar = "export_xml_channel", default = None,
                help = "Exports XML integration channel")
                
    parser.add_argument("-ij", "--import_json_channel", type = str, nargs = 1,
                    metavar = "import_json_channel", default = None,
                    help = "Imports integration channel")
    
    parser.add_argument("-ej", "--export_json_channel", type = str, nargs = 2,
                metavar = "export_json_channel", default = None,
                help = "Exports integration channel")
                
    parser.add_argument("-dl", "--delete_channel", type = str, nargs = 1,
            metavar = "delete_channel", default = None,
            help = "Deletes integration channel")
                
    # parse the arguments from standard input
    args = parser.parse_args()
     
    # calling functions depending on type of argument
    if args.deploy != None:
        deploy(args)
        
    if args.undeploy != None:
        undeploy(args)
        
    if args.import_xml_channel != None:
        import_xml_channel(args)
    
    if args.export_xml_channel != None:
        export_xml_channel(args)
        
    if args.import_json_channel != None:
        import_json_channel(args)
    
    if args.export_json_channel != None:
        export_json_channel(args)
    
    if args.delete_channel != None:
        delete_channel(args)
        
if __name__ == "__main__":
    # calling the main function
    main()