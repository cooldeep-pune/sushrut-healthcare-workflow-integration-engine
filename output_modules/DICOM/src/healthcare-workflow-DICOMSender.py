#!/usr/bin/env python
"""A Storage SCU application.
Used for transferring DICOM SOP Instances to a Storage SCP.
"""

import argparse
import os
from pathlib import Path
import sys
import time
import psycopg2

from pydicom import dcmread,dcmwrite
from pydicom.errors import InvalidDicomError
from pydicom.uid import (
    ExplicitVRLittleEndian,
    ImplicitVRLittleEndian,
    ExplicitVRBigEndian,
    DeflatedExplicitVRLittleEndian,
)

from pynetdicom import AE, StoragePresentationContexts
from pynetdicom.apps.common import setup_logging, get_files
from pynetdicom._globals import DEFAULT_MAX_LENGTH
from redis import Redis
from io import BytesIO

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
            

def _setup_argparser():
    """Setup the command line arguments"""
    # Description
    parser = argparse.ArgumentParser(
        description=(
            "The storescu application implements a Service Class User "
            "(SCU) for the Storage Service Class. For each DICOM "
            "file on the command line it sends a C-STORE message to a "
            "Storage Service Class Provider (SCP) and waits for a response."
        ),
        usage="storescu [options] addr port",
    )

    # Parameters
    req_opts = parser.add_argument_group("Parameters")
    req_opts.add_argument(
        "addr", help="TCP/IP address or hostname of DICOM peer", type=str
    )
    req_opts.add_argument("port", help="TCP/IP port number of peer", type=int)

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

    # Input Options
    in_opts = parser.add_argument_group("Input Options")
    in_opts.add_argument(
        "-r",
        "--recurse",
        help="recursively search the given directory",
        action="store_true",
    )

    # Network Options
    net_opts = parser.add_argument_group("Network Options")
    net_opts.add_argument(
        "-aet",
        "--calling-aet",
        metavar="[a]etitle",
        help="set my calling AE title (default: STORESCU)",
        type=str,
        default="STORESCU",
    )
    net_opts.add_argument(
        "-aec",
        "--called-aet",
        metavar="[a]etitle",
        help="set called AE title of peer (default: ANY-SCP)",
        type=str,
        default="ANY-SCP",
    )
    net_opts.add_argument(
        "-ta",
        "--acse-timeout",
        metavar="[s]econds",
        help="timeout for ACSE messages (default: 30 s)",
        type=float,
        default=90,
    )
    net_opts.add_argument(
        "-td",
        "--dimse-timeout",
        metavar="[s]econds",
        help="timeout for DIMSE messages (default: 30 s)",
        type=float,
        default=90,
    )
    net_opts.add_argument(
        "-tn",
        "--network-timeout",
        metavar="[s]econds",
        help="timeout for the network (default: 30 s)",
        type=float,
        default=90,
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

    # Transfer Syntaxes
    ts_opts = parser.add_argument_group("Transfer Syntax Options")
    syntax = ts_opts.add_mutually_exclusive_group()
    syntax.add_argument(
        "-xe",
        "--request-little",
        help="request explicit VR little endian TS only",
        action="store_true",
    )
    syntax.add_argument(
        "-xb",
        "--request-big",
        help="request explicit VR big endian TS only",
        action="store_true",
    )
    syntax.add_argument(
        "-xi",
        "--request-implicit",
        help="request implicit VR little endian TS only",
        action="store_true",
    )

    # Misc Options
    misc_opts = parser.add_argument_group("Miscellaneous Options")
    misc_opts.add_argument(
        "-cx",
        "--required-contexts",
        help=(
            "only request the presentation contexts required for the "
            "input DICOM file(s)"
        ),
        action="store_true",
    )

    channel_opts = parser.add_argument_group(description = "Integration channel Options")

    # defining arguments for parser object
    channel_opts.add_argument("-c", "--channel", type = str, nargs = 1,
                        metavar = "id", default = None,
                        help = "integration channel")
    return parser.parse_args()


def get_contexts(ds):
    """Return the valid DICOM files and their context values.
    Parameters
    ----------
    ds : DICOM data
        A list of paths to the files to try and get data from.
    Returns
    -------
    list of dict
        the {SOP Class UID :
        [Transfer Syntax UIDs]} that can be used to create the required
        presentation contexts.
    """
    contexts = {}

    try:
        sop_class = ds.SOPClassUID
        tsyntax = ds.file_meta.TransferSyntaxUID
    except Exception as exc:
        print('ERROR')
    tsyntaxes = contexts.setdefault(sop_class, [])
    if tsyntax not in tsyntaxes:
        tsyntaxes.append(tsyntax)

    return contexts


def main(args=None):
    """Run the application."""
    if args is not None:
        sys.argv = args

    args = _setup_argparser()

    if args.version:
        print(f"storescu.py v{__version__}")
        sys.exit()

    APP_LOGGER = setup_logging(args, "storescu")
    APP_LOGGER.debug(f"storescu.py v{__version__}")
    APP_LOGGER.debug("")

    ae = AE(ae_title=args.calling_aet)
    ae.acse_timeout = args.acse_timeout
    ae.dimse_timeout = args.dimse_timeout
    ae.network_timeout = args.network_timeout


    """  #Propose the default presentation contexts
    if args.request_little:
        transfer_syntax = [ExplicitVRLittleEndian]
    elif args.request_big:
        transfer_syntax = [ExplicitVRBigEndian]
    elif args.request_implicit:
        transfer_syntax = [ImplicitVRLittleEndian]
    else:
        transfer_syntax = [
            ExplicitVRLittleEndian,
            ImplicitVRLittleEndian,
            DeflatedExplicitVRLittleEndian,
            ExplicitVRBigEndian,
        ]

    for cx in StoragePresentationContexts:
        ae.add_requested_context(cx.abstract_syntax, transfer_syntax)
    """
    
    queue_name = "dest-" + args.channel[0]
    print(queue_name)

    ii = 1
    while True:
        msg = REDIS_CLIENT.rpop(queue_name)
        if msg is None:
            time.sleep(0.1)
            continue
        # Request association with remote
        print(f'data size in loop: {len((msg))}')
        APP_LOGGER.info(f"Sending file")
        try:
            ds = dcmread(BytesIO(msg),force=True)
            contexts = get_contexts(ds)
            
            for abstract, transfer in contexts.items():
                for tsyntax in transfer:
                    ae.add_requested_context(abstract, tsyntax)
            
            assoc = ae.associate(
                args.addr, args.port, ae_title=args.called_aet, max_pdu=args.max_pdu
            )
            if assoc.is_established:
                status = assoc.send_c_store(ds, ii)
                print(status)
                ii += 1
                assoc.release()
        except InvalidDicomError:
            APP_LOGGER.error(f"Bad DICOM file")
        except Exception as exc:
            APP_LOGGER.error(f"Store failed")
            APP_LOGGER.exception(exc)


    else:
        sys.exit(1)


if __name__ == "__main__":
    main()