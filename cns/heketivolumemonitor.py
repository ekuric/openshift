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
parser.add_argument("--delvol", help="number of volumes to delete")

args = parser.parse_args()

urllocation = args.urllocation
port = args.port
projectname = args.projectname
volfile = args.volfile
numvol = args.numvol
delvol = args.delvol

action = args.action


def delete_cns():
    response = urllib2.urlopen(urllocation)
    volumes = json.load(response)
    cnsvolumes = volumes.values()
    startvol = int(len(cnsvolumes[0])) -1
    endvol = int(len(cnsvolumes[0])) - int(delvol)
    # todo : make possible to delete stuff in multiple projects
    subprocess.call(["oc", "delete", "pods", "--all", "-n", projectname])
    subprocess.call(["oc", "delete", "pvc", "--all", "-n", projectname])

    ts = time.time()

    while int(len(cnsvolumes[0])) > int(startvol):
        with open(volfile, "a+") as currentvol:
            currentvol.write("Present %s CNS volumes, necessary to delete %d CNS volumes\r\n" % (str(len(cnsvolumes[0])), int(delvol)))
        response = urllib2.urlopen(urllocation)
        volumes = json.load(response)
        cnsvolumes = volumes.values()
        time.sleep(1)

    sd = time.time()

    while len(cnsvolumes[0]) >= endvol+1:
        response = urllib2.urlopen(urllocation)
        volumes = json.load(response)
        cnsvolumes = volumes.values()
        with open(volfile, "a+") as currentvol:
            currentvol.write("Delete started, necessary to delete %d CNS volumes\r\n" % int(delvol))
        time.sleep(1)

    te = time.time()

    with open(volfile, "a+")  as currentvol:
        currentvol.write("Deleted: %s\r\nDelete time: %s\r\nWait time before delete started: %s\r\n" % (int(delvol),  str(te-ts), str(sd-ts)))
    print ("Total CNS volumes deleted", int(delvol), "delete time", float(te-ts), "seconds")

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
            startvol.write("Number of running CNS volumes: %s\r\n" % str(len(cnsvolumes[0])), "waiting to start"
                                                                                              "additional", numvol, "CNS volumes")

        time.sleep (1)


    te = time.time()
    with open(volfile, "a+")  as startvol:
        startvol.write("Created: %s CNS volumes:\r\nTime: %s sec\r\nAverage: %s seconds for one CNS volume\n " % (str(numvol), str(te-ts), str(float(te-ts)/int(numvol))))


if __name__ == "__main__":
    if action == "create":
        create_cns()
    elif action == "delete":
        delete_cns()


