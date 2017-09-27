#!/usr/bin/env python

# python script to query heketi API - specifically /volumes and print number of volumes over time

import argparse
import urllib2
import json
import time
import subprocess
import sys
import datetime
import hashlib
import jwt

parser = argparse.ArgumentParser(description="Script to query specific URL and print output")
parser.add_argument("--urllocation", help="url to query", required=True )
parser.add_argument("--projectname", help="pvc project name", required=True)
parser.add_argument("--port", help="on what port to query, by default we will query on port 8080",default=8080, required=True)
parser.add_argument("--volfile", help="file to write heketi volumes number during delete", default="heketivol.txt")
parser.add_argument("--numvol", help="the number of volumes we want to create, we know this in advance", required=True)
parser.add_argument("--action", help="action can be delete or create")
parser.add_argument("--delvol", help="number of volumes to delete")
parser.add_argument("--secret", help="authentication secret", default=None)

args = parser.parse_args()

urllocation = args.urllocation
port = args.port
projectname = args.projectname
volfile = args.volfile
numvol = args.numvol
delvol = args.delvol

action = args.action
secret = args.secret

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
    cnsvolumes = get_volumes()

    ts = time.time()
    while len(cnsvolumes[0]) < int(numvol)+1:
        print ("Currently:", len(cnsvolumes[0]),"waiting to start", numvol, "CNS volumes")
        with open(volfile, "a+") as startvol:
            cnsvolumes = get_volumes()
            startvol.write("Number of running CNS volumes: %s\r\n"
                           "waiting to start additional %d CNS volumes\r\n" %
                           (str(len(cnsvolumes[0])),
                            int(numvol) + 1 - len(cnsvolumes[0])))

        time.sleep (1)


    te = time.time()
    with open(volfile, "a+")  as startvol:
        startvol.write("Created: %s CNS volumes:\r\nTime: %s sec\r\nAverage: %s seconds for one CNS volume\n " % (str(numvol), str(te-ts), str(float(te-ts)/int(numvol))))


def get_auth_code(method, uri, secret, user):
    claims = dict()
    claims['iss'] = user
    claims['iat'] = datetime.datetime.utcnow()
    claims['exp'] = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
    claims['qsh'] = hashlib.sha256(method + '&' + uri).hexdigest()

    return jwt.encode(claims, secret, algorithm='HS256')


def get_volumes():
    request = urllib2.Request(urllocation)
    if secret:
        request.add_header('Authorization', 'Bearer ' +
                           get_auth_code('GET', '/volumes', secret, 'admin'))
    response = urllib2.urlopen(request)
    volumes = json.load(response)
    return volumes.values()


if __name__ == "__main__":
    if action == "create":
        create_cns()
    elif action == "delete":
        delete_cns()


