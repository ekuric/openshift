#!/usr/bin/env python

# python script to query heketi API - specifically /volumes and print number of volumes over time

import argparse
import urllib2
import json
import time
import subprocess
import sys 

parser = argparse.ArgumentParser(description="Script to query specific URL and print output")
parser.add_argument("--urllocation", help="url to query", required=True )
parser.add_argument("--projectname", help="pvc project name", required=True)
parser.add_argument("--port", help="on what port to query, by default we will query on port 8080",default=8080, required=True)
parser.add_argument("--volfile", help="file to write heketi volumes number during delete", default="heketivol.txt")
parser.add_argument("--numvol", help="the number of volumes we want to create, we know this in advance")
parser.add_argument("--action", help="action can be delete or create")

args = parser.parse_args()

urllocation = args.urllocation
port = args.port
projectname = args.projectname
volfile = args.volfile
numvol = args.numvol

action = args.action


def delete_cns():
    response = urllib2.urlopen(urllocation)
    volumes = json.load(response)
    cnsvolumes = volumes.values()
    startvol = len(cnsvolumes[0])-1
    subprocess.call(["oc", "delete", "pvc", "--all", "-n", projectname])

    ts = time.time()

    while int(len(cnsvolumes[0])) > int(startvol):
        response = urllib2.urlopen(urllocation)
        volumes = json.load(response)
        cnsvolumes = volumes.values()
        with open(volfile, "a+") as currentvol:
            currentvol.write("CNS volumes delete not started - CNS volumes present: %s\r\n" % str(len(cnsvolumes[0])))
        time.sleep(1)

    sd = time.time()

    while len(cnsvolumes[0]) > 1:
        response = urllib2.urlopen(urllocation)
        volumes = json.load(response)
        cnsvolumes = volumes.values()
        with open(volfile, "a+") as currentvol:
            currentvol.write("CNS volume delete started - CNS volumes present %s\r\n" % str(len(cnsvolumes[0])))
        time.sleep(1)

    te = time.time()

    with open(volfile, "a+")  as currentvol:
        currentvol.write("Total deleted CNS volumes: %s\r\nTotal delete time: %s\r\nWait time before delete started: %s\r\n" % (str(startvol), str(te-ts), str(sd-ts)))


def create_cns():

    response = urllib2.urlopen(urllocation)
    volumes = json.load(response)
    cnsvolumes = volumes.values()

    ts = time.time()
    while len(cnsvolumes[0]) < int(numvol)+1:
        print ("Currently:", len(cnsvolumes[0]),"waiting to start", numvol, "CNS volumes")
        with open(volfile, "a+") as startvol:
            response = urllib2.urlopen(urllocation)
            volumes = json.load(response)
            cnsvolumes = volumes.values()
            startvol.write("Number of running CNS volumes: %s\r\n" % str(len(cnsvolumes[0])))

        time.sleep (1)


    te = time.time()
    with open(volfile, "a+")  as startvol:
        startvol.write("Created: %s CNS volumes:\r\nTime: %s sec\r\nAverage: %s seconds for one CNS volume\n " % (str(numvol), str(te-ts), str(float(te-ts)/int(numvol))))


if __name__ == "__main__":
    if action == "create":
        create_cns()
    elif action == "delete":
        delete_cns()


