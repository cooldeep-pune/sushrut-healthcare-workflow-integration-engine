#!/usr/bin/env python
"""A Storage SCP application.
Used for receiving DICOM SOP Instances transferred from an SCU.
"""

import argparse
import sys
from io import BytesIO
import psycopg2
import os

from pydicom import dcmread, dcmwrite
from pydicom.filebase import DicomFileLike
from pydicom.dataset import Dataset, FileMetaDataset

from pydicom.uid import (
    ExplicitVRLittleEndian,
    ImplicitVRLittleEndian,
    ExplicitVRBigEndian,
    JPEG2000Lossless,
    JPEG2000,
)
import time
from redis import Redis
from os import SEEK_END
from functools import partial


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
    json_channel = get_channle_json(channel_id)
    if "transformer" in json_channel['channel']['sourceConnector']:
        queue_name = "trans-" + channel_id
    else:
        queue_name = "dest-" + channel_id
    print(queue_name)
    REDIS_CLIENT.rpush(queue_name,*values)

    
      
from pynetdicom import (
    AE,
    evt,
    AllStoragePresentationContexts,
    VerificationPresentationContexts,
)
from pynetdicom.apps.common import setup_logging
from pynetdicom._globals import ALL_TRANSFER_SYNTAXES, DEFAULT_MAX_LENGTH


__version__ = "0.6.0"

def handle_store(event, args, app_logger):
    """Handle a C-STORE request event."""
    # Decode the C-STORE request's *Data Set* parameter to a pydicom Dataset
    ds = event.dataset
    ds.file_meta = event.file_meta
    
    # add inline filter
    
    with BytesIO() as buffer:
        # create a DicomFileLike object that has some properties of DataSet
        memory_dataset = DicomFileLike(buffer)
        # write the dataset to the DicomFileLike object
        dcmwrite(memory_dataset, ds)
        
        memory_dataset.seek(0)

        push(args.channel[0],memory_dataset.read())
    # Return a 'Success' status
    return 0x0000
 
def _setup_argparser():
    """Setup the command line arguments"""
    # Description
    parser = argparse.ArgumentParser(
        description=(
            "The storescp application implements a Service Class "
            "Provider (SCP) for the Storage and Verification SOP Classes. It "
            "listens for a DICOM C-STORE message from a Service Class User "
            "(SCU) and stores the resulting DICOM dataset."
        ),
        usage="storescp [options] port",
    )

    # Parameters
    req_opts = parser.add_argument_group("Parameters")
    req_opts.add_argument("port", help="TCP/IP port number to listen on", type=int)

    # General Options
    gen_opts = parser.add_argument_group("General Options")
    gen_opts.add_argument(
        "--version", help="print version information and exit", action="store_true"
    )
    output = gen_opts.add_mutually_exclusive_group()
    output.add_argument(
        "-q",
        "--quiet",
        help="quiet mode, print no warnings and errors",
        action="store_const",
        dest="log_type",
        const="q",
    )
    output.add_argument(
        "-v",
        "--verbose",
        help="verbose mode, print processing details",
        action="store_const",
        dest="log_type",
        const="v",
    )
    output.add_argument(
        "-d",
        "--debug",
        help="debug mode, print debug information",
        action="store_const",
        dest="log_type",
        const="d",
    )
    gen_opts.add_argument(
        "-ll",
        "--log-level",
        metavar="[l]",
        help=("use level l for the logger (critical, error, warn, info, debug)"),
        type=str,
        choices=["critical", "error", "warn", "info", "debug"],
    )

    # Network Options
    net_opts = parser.add_argument_group("Network Options")
    net_opts.add_argument(
        "-aet",
        "--ae-title",
        metavar="[a]etitle",
        help="set my AE title (default: STORESCP)",
        type=str,
        default="STORESCP",
    )
    net_opts.add_argument(
        "-ta",
        "--acse-timeout",
        metavar="[s]econds",
        help="timeout for ACSE messages (default: 30 s)",
        type=float,
        default=900,
    )
    net_opts.add_argument(
        "-td",
        "--dimse-timeout",
        metavar="[s]econds",
        help="timeout for DIMSE messages (default: 30 s)",
        type=float,
        default=900,
    )
    net_opts.add_argument(
        "-tn",
        "--network-timeout",
        metavar="[s]econds",
        help="timeout for the network (default: 30 s)",
        type=float,
        default=900,
    )
    net_opts.add_argument(
        "-pdu",
        "--max-pdu",
        metavar="[n]umber of bytes",
        help=(
            f"set max receive pdu to n bytes (0 for unlimited, "
            f"default: {DEFAULT_MAX_LENGTH})"
        ),
        type=int,
        default=DEFAULT_MAX_LENGTH,
    )
    net_opts.add_argument(
        "-ba",
        "--bind-address",
        metavar="[a]ddress",
        help=(
            "The address of the network interface to "
            "listen on. If unset, listen on all interfaces."
        ),
        default="",
    )

    # Transfer Syntaxes
    ts_opts = parser.add_argument_group("Preferred Transfer Syntaxes")
    ts = ts_opts.add_mutually_exclusive_group()
    ts.add_argument(
        "-x=",
        "--prefer-uncompr",
        help="prefer explicit VR local byte order",
        action="store_true",
    )
    ts.add_argument(
        "-xe",
        "--prefer-little",
        help="prefer explicit VR little endian TS",
        action="store_true",
    )
    ts.add_argument(
        "-xb",
        "--prefer-big",
        help="prefer explicit VR big endian TS",
        action="store_true",
    )
    ts.add_argument(
        "-xi",
        "--implicit",
        help="accept implicit VR little endian TS only",
        action="store_true",
    )

    # Output Options
    out_opts = parser.add_argument_group("Output Options")
    out_opts.add_argument(
        "-od",
        "--output-directory",
        metavar="[d]irectory",
        help="write received objects to directory d",
        type=str,
    )
    out_opts.add_argument(
        "--ignore", help="receive data but don't store it", action="store_true"
    )

    # Miscellaneous Options
    misc_opts = parser.add_argument_group("Miscellaneous Options")
    misc_opts.add_argument(
        "--no-echo", help="don't act as a verification SCP", action="store_true"
    )


    channel_opts = parser.add_argument_group(description = "Integration channel Options")

    # defining arguments for parser object
    channel_opts.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "id", default = None,
                        help = "integration channel")
                        
    return parser.parse_args()


def main(args=None):
    """ Initialize redis """
    
   
    """Run the application."""
    if args is not None:
        sys.argv = args

    args = _setup_argparser()
    if args.version:
        print(f"storescp.py v{__version__}")
        sys.exit()

    APP_LOGGER = setup_logging(args, "storescp")
    APP_LOGGER.debug(f"storescp.py v{__version__}")
    APP_LOGGER.debug("")

    # Set Transfer Syntax options
    transfer_syntax = ALL_TRANSFER_SYNTAXES[:]

    if args.prefer_uncompr:
        transfer_syntax.remove(ImplicitVRLittleEndian)
        transfer_syntax.append(ImplicitVRLittleEndian)
    elif args.prefer_little:
        transfer_syntax.remove(ExplicitVRLittleEndian)
        transfer_syntax.insert(0, ExplicitVRLittleEndian)
    elif args.prefer_big:
        transfer_syntax.remove(ExplicitVRBigEndian)
        transfer_syntax.insert(0, ExplicitVRBigEndian)
    elif args.implicit:
        transfer_syntax = [ImplicitVRLittleEndian]
    
    # Compress images
    
    transfer_syntax.append(JPEG2000Lossless)
    
    transfer_syntax.append(JPEG2000)
    
    
    
    handlers = [(evt.EVT_C_STORE, handle_store, [args, APP_LOGGER])]

    # Create application entity
    ae = AE(ae_title=args.ae_title)

    # Add presentation contexts with specified transfer syntaxes
    for context in AllStoragePresentationContexts:
        ae.add_supported_context(context.abstract_syntax, transfer_syntax)

    if not args.no_echo:
        for context in VerificationPresentationContexts:
            ae.add_supported_context(context.abstract_syntax, transfer_syntax)

    ae.maximum_pdu_size = args.max_pdu

    # Set timeouts
    ae.network_timeout = args.network_timeout
    ae.acse_timeout = args.acse_timeout
    ae.dimse_timeout = args.dimse_timeout
    
    ae.start_server((args.bind_address, args.port), evt_handlers=handlers)


if __name__ == "__main__":
    main()