#bin/python3

import os
import json
import requests
import decimal as dec
import datetime as dt
from collections import namedtuple

# Constants
encoding = 'utf8'
atto = 1e18
api_base = 'https://api.s%d.t.hmny.io'

# Container for Address & Shard
FoundationalNode = namedtuple('FoundationalNode', ['address', 'shard'])

# RPC request generators
# Generates RPC request fields for getting current balance of an address
def current_balance_request(addr) -> dict:
    return {"id": "1", "jsonrpc": "2.0",
            "method": "hmy_getBalance",
            "params": [addr, "latest"]}

# Read csv of foundational node addresses & shards generated by collect_addresses.py
# Give absolute path to the address_file
def read_addresses(address_file) -> list:
    # Check file exist
    if not os.path.exists(address_file):
        print("Error: File does not exist %s", args.address_list)
        os.exit(-1)
    with open(address_file, 'r') as f:
        address_list = [FoundationalNode(*(x.strip().split(','))) for x in f]
    # Check list of FoundationalNodes
    if len(address_list) < 1:
        print("Error: Address list is empty.\nFile is empty or incorrectly formatted.")
        os.exit(-1)
    return address_list

# Send RPC request
# Take API endpoint & request body (as dict)
# Returns JSON format reply, None if errors
def request(endpoint, request, output = False) -> str:
    # Send request
    r = requests.get(endpoint, headers = {'Content-Type':'application/json; charset=utf8'}, data = request)
    # Check for invalid status code
    if r.status_code != 200:
        print("Error: Return status code %s" % r.status_code)
        return None

    # Check for valid JSON format return
    try:
        r.json()
    except ValueError:
        print("Error: Unable to read JSON reply")
        return None

    return r.json()

# Format returned balance value
def format_balance(hex_balance) -> dec.Decimal:
    dec_balance = int(hex_balance, 16)

    return dec.Decimal(dec_balance) / dec.Decimal(atto)

# Round time to the nearest 15 minutes
def round_time(t) -> dt.datetime:
    interval = dt.timedelta(minutes = 15).total_seconds()

    seconds = (t - t.min).seconds
    rounding = (seconds + interval / 2) // interval * interval
    return t + dt.timedelta(0, rounding - seconds, -t.microsecond)