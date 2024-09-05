import docker
import socket,os
import argparse
import psycopg2
import os

def load_channel(
    channel_id: str
):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(host= os.environ['POSTGRES_HOST'],database=os.environ['POSTGRES_DB'],user=os.environ['POSTGRES_USER'],password=os.environ['POSTGRES_PASSWORD'],port=int(os.environ['POSTGRES_PORT']))
        
        select_sql = "select content from healthcare_channels WHERE channel_id=%s;"
        # create a cursor
        cur_select = conn.cursor()
        cur_select.execute(select_sql,(channel_id,))
        result = cur_select.fetchone()[0]
        cur_select.close()
        
        return result
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed.')
            
def startTransformer(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    transformerDockerContainer= json_channel['channel']['sourceConnector']['transformer']['@class']
    transformerDockerContainerName= json_channel['channel']['sourceConnector']['transformer']['@class'].replace('/','-') + "-" + channel_id
    print('starting transformer '+transformerDockerContainerName)
    containers = client.containers.list(filters={'name':transformerDockerContainerName})

    for container in containers:
        container.stop()
        container.remove()
        
    client.containers.run(transformerDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=transformerDockerContainerName,environment=env_list,detach=True)
    
def startIOStreamdestinationConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    destinationDockerContainer = json_channel['channel']['destinationConnectors']['connector']['properties']['@class']
    destinationDockerContainerName = destinationDockerContainer.replace('/','-') + "-" + channel_id
    print('starting destination connector '+destinationDockerContainerName)
    
    containers = client.containers.list(filters={'name':destinationDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(destinationDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=destinationDockerContainerName,environment=env_list,detach=True)
    
def startHTTPdestinationConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    destinationDockerContainer = json_channel['channel']['destinationConnectors']['connector']['properties']['@class']
    destinationDockerContainerName = destinationDockerContainer.replace('/','-') + "-" + channel_id
    print('starting destination connector '+destinationDockerContainerName)
    
    containers = client.containers.list(filters={'name':destinationDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(destinationDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=destinationDockerContainerName,environment=env_list,detach=True)
    
def startHTTPSdestinationConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    destinationDockerContainer = json_channel['channel']['destinationConnectors']['connector']['properties']['@class']
    destinationDockerContainerName = destinationDockerContainer.replace('/','-') + "-" + channel_id
    print('starting destination connector '+destinationDockerContainerName)
    
    containers = client.containers.list(filters={'name':destinationDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(destinationDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=destinationDockerContainerName,environment=env_list,detach=True)

def startHL7destinationConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    destinationDockerContainer = json_channel['channel']['destinationConnectors']['connector']['properties']['@class']
    destinationDockerContainerName = destinationDockerContainer.replace('/','-') + "-" + channel_id
    print('starting destination connector '+destinationDockerContainerName)
    
    containers = client.containers.list(filters={'name':destinationDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(destinationDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=destinationDockerContainerName,environment=env_list,detach=True)
    

def startDICOMdestinationConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    destinationDockerContainer = json_channel['channel']['destinationConnectors']['connector']['properties']['@class']
    destinationDockerContainerName = destinationDockerContainer.replace('/','-') + "-" + channel_id
    print('starting destination connector '+destinationDockerContainerName)
    
    containers = client.containers.list(filters={'name':destinationDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(destinationDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=destinationDockerContainerName,environment=env_list,detach=True)

def startIOStreamsourceConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    sourceDockerContainer = json_channel['channel']['sourceConnector']['properties']['@class']
    sourceDockerContainerName = sourceDockerContainer.replace('/','-') + "-" + channel_id
    
    print('starting source connector '+sourceDockerContainerName)
    
    containers = client.containers.list(filters={'name':sourceDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(sourceDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=sourceDockerContainerName,environment=env_list,detach=True)
    
def startDICOMsourceConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    sourceDockerContainer = json_channel['channel']['sourceConnector']['properties']['@class']
    sourceDockerContainerName = sourceDockerContainer.replace('/','-') + "-" + channel_id
    
    print('starting source connector '+sourceDockerContainerName)
    
    src_port = json_channel['channel']['sourceConnector']['properties']['listenerConnectorProperties']['port']
    containers = client.containers.list(filters={'name':sourceDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(sourceDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=sourceDockerContainerName,ports={src_port+'/tcp': int(src_port)},environment=env_list,detach=True)

def startHTTPsourceConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    sourceDockerContainer = json_channel['channel']['sourceConnector']['properties']['@class']
    sourceDockerContainerName = sourceDockerContainer.replace('/','-') + "-" + channel_id
    
    print('starting source connector '+sourceDockerContainerName)
    
    src_port = json_channel['channel']['sourceConnector']['properties']['listenerConnectorProperties']['port']
    containers = client.containers.list(filters={'name':sourceDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(sourceDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=sourceDockerContainerName,ports={src_port+'/tcp': int(src_port)},environment=env_list,detach=True)

def startHTTPSsourceConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    sourceDockerContainer = json_channel['channel']['sourceConnector']['properties']['@class']
    sourceDockerContainerName = sourceDockerContainer.replace('/','-') + "-" + channel_id
    
    print('starting source connector '+sourceDockerContainerName)
    
    src_port = json_channel['channel']['sourceConnector']['properties']['listenerConnectorProperties']['port']
    containers = client.containers.list(filters={'name':sourceDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(sourceDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=sourceDockerContainerName,ports={src_port+'/tcp': int(src_port)},environment=env_list,detach=True)
    
    
def startHL7sourceConnector(
    env_list:list,
    channel_id: str,
    json_channel: dict,
    client
):
    sourceDockerContainer = json_channel['channel']['sourceConnector']['properties']['@class']
    sourceDockerContainerName = sourceDockerContainer.replace('/','-') + "-" + channel_id
    
    print('starting source connector '+sourceDockerContainerName)
    
    src_port = json_channel['channel']['sourceConnector']['properties']['listenerConnectorProperties']['port']
    containers = client.containers.list(filters={'name':sourceDockerContainerName})
    
    for container in containers:
        container.stop()
        container.remove()
    
    client.containers.run(sourceDockerContainer, "python3 /opt/healthcare-workflow/Exec.py -c " + channel_id,name=sourceDockerContainerName,ports={src_port+'/tcp': int(src_port)},environment=env_list,detach=True)

def get_env_list():
    env_list=[]
    env_list.append('POSTGRES_HOST='+ os.environ['POSTGRES_HOST'])
    env_list.append('POSTGRES_USER='+ os.environ['POSTGRES_USER'])
    env_list.append('POSTGRES_PASSWORD='+ os.environ['POSTGRES_PASSWORD'])
    env_list.append('POSTGRES_DB='+ os.environ['POSTGRES_DB'])
    env_list.append('POSTGRES_PORT='+ os.environ['POSTGRES_PORT'])
    env_list.append('ORCHESTRATOR_HOST='+ os.environ['ORCHESTRATOR_HOST'])
    env_list.append('ORCHESTRATOR_PORT='+ os.environ['ORCHESTRATOR_PORT'])
    env_list.append('REDIS_HOST='+ os.environ['REDIS_HOST'])
    env_list.append('REDIS_PORT='+ os.environ['REDIS_PORT'])
    return env_list

def run(
    channel_id: str
) -> None:
    try:
        print('starting docker containers for channel' + channel_id)
        
        json_channel = load_channel(channel_id)
        
        tls_config = docker.tls.TLSConfig(ca_cert='/docker/cert.pem') # local host /mnt/c/workspace/keys/docker/cert.pem
        client = docker.DockerClient(base_url='unix://var/run/docker.sock',tls=tls_config)

        print('Get Environment List')
        env_list = get_env_list()
        print(env_list)
        """ start input connector """
        srcConnector = json_channel['channel']['sourceConnector']['transportName']
        print(srcConnector)
        if srcConnector == "DICOM Listener":
            startDICOMsourceConnector(env_list,channel_id,json_channel,client)
        elif srcConnector == "HTTP Listener":
            startHTTPsourceConnector(env_list,channel_id,json_channel,client)
        elif srcConnector.lower()== "HL7 Listener".lower():
            startHL7sourceConnector(env_list,channel_id,json_channel,client)
        elif srcConnector.lower()== "IOStream Reader".lower():
            startIOStreamsourceConnector(env_list,channel_id,json_channel,client)
        elif srcConnector == "HTTPS Listener":
            startHTTPSsourceConnector(env_list,channel_id,json_channel,client)
        
        """ start output connector """
        destConnector = json_channel['channel']['destinationConnectors']['connector']['transportName']
        print(destConnector)
        if destConnector == "DICOM Sender":
            startDICOMdestinationConnector(env_list,channel_id,json_channel,client)
        elif destConnector == "HTTP Sender":
            startHTTPdestinationConnector(env_list,channel_id,json_channel,client)
        elif destConnector == "HL7 Sender":
            startHL7destinationConnector(env_list,channel_id,json_channel,client)
        elif destConnector == "IOStream Writer":
            startIOStreamdestinationConnector(env_list,channel_id,json_channel,client)
        elif destConnector == "HTTPS Sender":
            startHTTPSdestinationConnector(env_list,channel_id,json_channel,client)
            
        if "transformer" in json_channel['channel']['sourceConnector']:
            startTransformer(env_list,channel_id,json_channel,client)
    except Exception as error:
        print('Error in docker client'+ error)
        
def stop(
    channel_id: str
):
    try:
        print('stopping docker containers for channel '+channel_id)
        
        json_channel = load_channel(channel_id)

        tls_config = docker.tls.TLSConfig(ca_cert='/docker/cert.pem') # local host /mnt/c/workspace/keys/docker/cert.pem
        client = docker.DockerClient(base_url='unix://var/run/docker.sock',tls=tls_config)

        sourceDockerContainer = json_channel['channel']['sourceConnector']['properties']['@class']
        sourceDockerContainerName = sourceDockerContainer.replace('/','-') + "-" + channel_id
        
        print('stopping source connector '+sourceDockerContainerName)
        
        containers = client.containers.list(filters={'name':sourceDockerContainerName})
        
        for container in containers:
            container.stop()
            container.remove()
            
        destinationDockerContainer = json_channel['channel']['destinationConnectors']['connector']['properties']['@class']
        destinationDockerContainerName = destinationDockerContainer.replace('/','-') + "-" + channel_id
        
        print('stopping destination connector '+destinationDockerContainerName)
        
        containers = client.containers.list(filters={'name':destinationDockerContainerName})
        
        for container in containers:
            container.stop()
            container.remove()
            
        if "transformer" in json_channel['channel']['sourceConnector']:
            transformerDockerContainer= json_channel['channel']['sourceConnector']['transformer']['@class']
            transformerDockerContainerName= json_channel['channel']['sourceConnector']['transformer']['@class'].replace('/','-') + "-" + channel_id
            print('stopping transformer '+transformerDockerContainerName)
            containers = client.containers.list(filters={'name':transformerDockerContainerName})

            for container in containers:
                container.stop()
                container.remove()
    except Exception as error:
        print('Error in docker client'+ error)
        
def execute(
    command: str
):
    words = command.split()
    if words[0] == "stop" :
        stop(words[1])
    elif words[0] == "run" :
        run(words[1])
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "A cli for integration engine!")

    # defining arguments for parser object
    parser.add_argument("-p", "--port", type = str, nargs = 1,
                        metavar = "port", default = None,
                        help = "orchestrator port")
                        
    args = parser.parse_args() 
    print(os.environ['ORCHESTRATOR_HOST'])
    print(os.environ['ORCHESTRATOR_PORT'])
    if args.port != None:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
        sock.bind(("", int(os.environ['ORCHESTRATOR_PORT'])))  
        sock.listen(5)  
        while True:
            try:
                connection,address = sock.accept()
                print(address)
                print(connection)
                buf = connection.recv(1024)
                print(buf)
                execute(buf.decode("utf-8"))
                connection.send(buf)    		
                connection.close()
            except Exception as error:
                print('Error in connection'+ error)