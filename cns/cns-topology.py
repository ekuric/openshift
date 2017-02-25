#!/usr/bin/env python

# script accepts yaml version of cns topology file, I find yaml more convenient than json ...  that is why this
# and generates topology.json which can be later used for cns setup
# CNS means -  Container Native Storage

import argparse
import yaml
import json

parser = argparse.ArgumentParser(description="Script to generate topology.json CNS topology file")
parser.add_argument("--cnsnodesfile", help="File containing list of servers to be used for CNS cluster", required=True)
args = parser.parse_args()

cnsnodesfile = args.cnsnodesfile
outfile = "topology.json"

with open(cnsnodesfile) as nodfile:
    jsonfs =  yaml.load(nodfile)
    with open(outfile, 'w') as outputfile:
        json.dump(jsonfs,outputfile, indent=4)
