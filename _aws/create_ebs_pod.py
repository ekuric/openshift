#!/usr/bin/env python 

# program to create OSE 3 pods with Amazon EC2 volumes as persistent storage 
# License GPL2/3 

__author__ = "elko"

import argparse
import boto3
import subprocess
import os
import json
import time 


class CreateEbs():

    def __init__(self,volumesize,vtype,region,tagprefix,mountpoint,image,pvfile,pvcfile,podfile,minpod,maxpod):

        self.volumesize = volumesize
        self.vtype = vtype
        self.region = region
        self.tagprefix = tagprefix
        self.mountpoint = mountpoint 
        self.image = image
        self.pvfile = pvfile
        self.pvcfile = pvcfile
        self.podfile = podfile
        self.minpod = minpod
        self.maxpod = maxpod
        session = boto3.Session(region_name=region)
        ec2 = boto3.resource("ec2")

    # create EC2 volume to be used later for pv/pvc and pod 
    # we create one EBS at time and tag it. Tags are only used for easier
    # retreival when we want to delete EBSes

    def ec2_volume(self,volumesize,vtype,region,tagprefix,mountpoint):

        self.volumesize = 1
        self.vtype = vtype  
        self.region = "us-west-2b"
        self.tagprefix = tagprefix
        self.mountpoint = "/mnt/persistentvolume"
        global tags
        global volumeid 

        session = boto3.Session(region_name=region)
        ec2 = boto3.resource("ec2")
        volume = ec2.create_volume(VolumeType=vtype,
                                       AvailabilityZone=region,
                                       Size=volumesize)

        volumeid = volume.id

        # volume created ... tag it for easier finding later - based on this tag
        # eventually, write volume.id to file and not use tagging - to reduce load on Amazon EC2 API 
        # more http://docs.aws.amazon.com/AWSEC2/latest/APIReference/query-api-troubleshooting.html#api-request-rate 
        # adding time.sleep(10) - however this does not solve problem fully 
        print ("Sleep 10 seconds before tagging volume")
        time.sleep(10)

        tags = ec2.create_tags(DryRun=False, Resources=[volume.id],
                                   Tags=[
                                       {'Key': tagprefix + volume.id,
                                        'Value': tagprefix
                                        },
                                   ])
    # create persistent volume 
    def pvolume(self,pvfile):

        self.pvfile = pvfile
        try:
            pvhandler = open(pvfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file... check input parameters")

        # file is opened, now, json load it 
        pvjson = json.load(pvhandler)
        
        pvvanila = { "metadata": {"name": "pvolume" + str(minpod) },
                     'spec': {'capacity': {'storage': volumesize },
                              'persistentVolumeReclaimPolicy': 'Recycle', 'accessModes': ['ReadWriteOnce'],
                              'awsElasticBlockStore': {'volumeid': volumeid , 'fsType': 'ext4'}}}
        pvjson.update(pvvanila)
        json.dump(pvjson, open("pvfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
        subprocess.call(["oc", "create", "-f", "pvfile.json"])
        os.remove("pvfile.json")

    # create persistent volume claim 
    def pclaim(self,pvcfile):

        self.pvcfile = pvcfile
        try:
            pvchandler = open(pvcfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file ... check input parameters")


        pvcjson = json.load(pvchandler)
        pvcvanila = {'metadata': {"name":"pvclaim" + str(minpod)},
                          'spec': {'accessModes': ['ReadWriteOnce'], 'resources': {'requests': {'storage': volumesize }}}}
        pvcjson.update(pvcvanila)
        json.dump(pvcjson, open("pvcfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
        subprocess.call(["oc", "create", "-f", "pvcfile.json" ])
        os.remove("pvcfile.json")

    # create pod 
    def ppod(self,image,maxpod,minpod,podfile):

        self.image = image 
        self.maxpod = maxpod 
        self.minpod = minpod 
        self.podfile = podfile 

        try:
            podfile = open(self.podfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file ... check input parameters")

        podjson = json.load(podfile)
        podvanila = {'metadata': {'name': "pod" + str(minpod)},
                         'spec': {'containers': [{'image': image,
                                                  'imagePullPolicy': 'IfNotPresent',
                                                  'name': "pod" + str(minpod),
                                                  'volumeMounts': [{'name': 'pvolume' + str(minpod),
                                                  'mountPath': mountpoint }]}],
                                                  'volumes': [{'persistentVolumeClaim': {'claimName': "pvclaim" + str(minpod)}, 'name': "pvolume" + str(minpod)}]}}
        podjson.update(podvanila)
        json.dump(podjson,  open("podfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
        subprocess.call(["oc", "create", "-f", "podfile.json"])
        os.remove("podfile.json")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Script to create OSE pods and attach one EBS volume per pod as persistent storage")
    parser.add_argument("--volumesize", help="size of EBS voluems - in GB ", default=5, type=int)
    parser.add_argument("--vtype", help="EBS volume type, default is gp2", default="gp2")
    parser.add_argument("--region", help="Amazon region where to connect", default="us-west-2b")
    parser.add_argument("--image", help="docker image to use", default="r7perffio")
    parser.add_argument("--tagprefix", help="tag prefix for EBS volumes, default tag is openshift-testing-EBS_volume_id", default="openshift-testing")
    parser.add_argument("--mountpoint", help="mount point inside pod where EBS volume will be mounted, default is /mnt/persistentvolume", default="/mnt/persistentvolume")
    parser.add_argument("--minpod", help="minimum number of pods to create - default is 1 - so minimum one pod will be created", type=int, default=1)
    parser.add_argument("--action", help="what to do  - either to create pods or delete pods", default="create")

    # required arguments
    parser.add_argument("--maxpod", help="maximum number of pods to create - required parameter", type=int, required=True)
    parser.add_argument("--pvfile", help="persistent volume definition json file - required parameter", required=True)
    parser.add_argument("--pvcfile", help="persistent volume claim definition json file - required parameter", required=True)
    parser.add_argument("--podfile", help="pod definition json file - required parameter", required=True)

    args = parser.parse_args()

    volumesize = args.volumesize
    vtype = args.vtype
    region = args.region
    image = args.image 
    tagprefix = args.tagprefix
    mountpoint = args.mountpoint
    minpod = args.minpod 
    maxpod = args.maxpod 
    pvfile = args.pvfile
    pvcfile = args.pvcfile
    podfile = args.podfile
    action = args.action
    
    create_ebs = CreateEbs(volumesize,vtype,region,tagprefix,mountpoint,image,pvfile,pvcfile,podfile,minpod,maxpod)
    total_pods = maxpod - minpod 
    while minpod < maxpod:
        create_ebs.ec2_volume(volumesize,vtype,region,tagprefix,mountpoint)
        create_ebs.pvolume(pvfile)
        create_ebs.pclaim(pvcfile)
        create_ebs.ppod(image,maxpod,minpod,podfile)
        minpod = minpod + 1 
    
    print ( total_pods , "pods which use EBS as pessistent storage are created")


