#!/usr/bin/env python

# python script to query heketi API - specifically /volumes and print number of volumes over time
#

import argparse
import urllib2
import json
import time
import subprocess

parser = argparse.ArgumentParser(description="Script to query Heketi service URL in order to get number of heketi volumes")
parser.add_argument("--urllocation", help="Heketi service URL", required=True )
parser.add_argument("--projectname", help="pvc project name", required=True)
parser.add_argument("--port", help="Heketi service port",default=8080, required=True)
parser.add_argument("--volfile", help="Output file where to write changes in number of heketi volumes",required=True, default="heketivol.txt")
parser.add_argument("--numvol", help="How many heketi volumes is expected to be created")
parser.add_argument("--action", help="either : create , or delete", required=True)
parser.add_argument("--timeout", help="timeout how often to query heketi /volumes endpoint, default is 1s", default=1)

args = parser.parse_args()

urllocation = args.urllocation
port = args.port
projectname = args.projectname
volfile = args.volfile
numvol = args.numvol
action = args.action
timeout = args.timeout


def delete_cns():
    # delete all PVC in particular project - this will trigger PV and CNS volume delete - dynamic provision case
    subprocess.call(["oc", "delete", "pvc", "--all", "-n", projectname])

    response = urllib2.urlopen(urllocation)
    volumes = json.load(response)
    totalvolumes = volumes.values()-1

    ts = time.time()

    while len(cnsvolumes[0]) > 1:
        print ("Currently:", len(cnsvolumes[0]), "cns volumes present,sleeping 1 second")
        with open(volfile, "a+") as currentvol:
            response = urllib2.urlopen(urllocation)
            volumes = json.load(response)
            cnsvolumes = volumes.values()
            currentvol.write("Number of running CNS volumes: %s\r\n" % str(len(cnsvolumes[0])))

        time.sleep(timeout)

    te = time.time()
    with open(volfile, "a+")  as currentvol:
        currentvol.write("Deleted %s CNS volumes:\r\nTime to delete: %s\r\n" % (str(totalvolumes), str(te-ts)))

def create_cns():

    response = urllib2.urlopen(urllocation)
    ts = time.time()
    volumes = json.load(response)
    cnsvolumes = volumes.values()

    while len(cnsvolumes[0]) < int(numvol)+1:
        print ("Currently:", len(cnsvolumes[0]),"waiting to start", numvol, "CNS volumes")
        with open(volfile, "a+") as startvol:
            response = urllib2.urlopen(urllocation)
            volumes = json.load(response)
            cnsvolumes = volumes.values()
            startvol.write("Number of running CNS volumes: %s\r\n" % str(len(cnsvolumes[0])))

        time.sleep (timeout)


    te = time.time()
    with open(volfile, "a+")  as startvol:
        startvol.write("Created: %s CNS volumes:\r\nTime: %s sec\r\nAverage: %s seconds for one CNS volume\n " % (str(numvol), str(te-ts), str(float(te-ts)/int(numvol))))

if __name__ == "__main__":
    if action == "create":
        create_cns()
    elif action == "delete":
        delete_cns()


