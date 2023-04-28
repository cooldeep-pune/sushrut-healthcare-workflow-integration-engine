#!/usr/bin/env python3
"""An example HTTP server with GET and POST endpoints."""
from http import HTTPStatus
import json
import time
import argparse
import psycopg2
import json
from redis import Redis
from functools import partial
import os
import http.client
from urllib.parse import urlparse
import ssl
def run_sender():

    parser = argparse.ArgumentParser(description = "Integration engine!")

    parser.add_argument("-u", "--url", type = str, nargs = 1,
                        metavar = "url", default = None,
                        help = "http/https url")
                        
    parser.add_argument("-j", "--json", type = str, nargs = 1,
                        metavar = "json", default = None,
                        help = "json payload")
                        
    # parse the arguments from standard input
    args = parser.parse_args()

    url = args.url[0]
    try:
        value_dict = json.loads(args.json[0])
        request_headers = {'Content-Type': 'application/json'}   
        posturl = urlparse(url)
        # Define the client certificate settings for https connection
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain('/opt/certs/client-cert.pem','/opt/certs/client-key.pem')
        context.load_verify_locations('/opt/certs/ca-cert.pem')        
        # Create a connection to submit HTTP requests
        connection = http.client.HTTPSConnection(posturl.hostname, port=posturl.port, context=context)
         
        # Use connection to submit a HTTP POST request
        connection.request(method="POST", url=url, headers=request_headers, body=args.json[0])
         
        # Print the HTTP response from the IOT service endpoint
        response = connection.getresponse()
        print(response.status, response.reason)
        data = response.read()
        print(data)
    except Exception as exc:
        print(f"Store failed")
        print(exc)
    

if __name__ == '__main__':
    run_sender()