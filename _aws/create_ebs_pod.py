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

    def __init__(self):

        print ("Program to create EBS volume and pv/pvc based on EBS")

    # create EC2 volume to be used later for pv/pvc and pod 
    # we create one EBS at time and tag it. Tags are only used for easier
    # retreival when we want to delete EBSes

    def ec2_volume(self,volumesize,vtype,region,tagprefix):

        self.volumesize = volumesize
        self.vtype = vtype  
        self.region = region 
        self.tagprefix = tagprefix

        global tags
        global volumeid
        ec2 = boto3.resource("ec2")

        volume = ec2.create_volume(VolumeType=vtype,
                                       AvailabilityZone=region,
                                       Size=volumesize)

        volumeid = volume.id

        # volume created ... tag it for easier finding later - based on this tag
        # eventually, write volume.id to file and not use tagging - to reduce load on Amazon EC2 API 
        # more http://docs.aws.amazon.com/AWSEC2/latest/APIReference/query-api-troubleshooting.html#api-request-rate 
        # adding time.sleep(10) - however this does not solve problem fully, but it is working workaround  
        print ("Sleep 10 seconds before tagging volume")
        time.sleep(10)

        tags = ec2.create_tags(DryRun=False, Resources=[volume.id],
                                   Tags=[
                                       {'Key': tagprefix + volume.id,
                                        'Value': tagprefix
                                        },
                                   ])
    # create persistent volume 
    # introduce check to stop if pvclaim is bigger than pvsize - cannot allocated such space 

    def pvolume(self,pvfile,pvsize):

        self.pvfile = pvfile
        try:
            pvhandler = open(pvfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file... check input parameters")

        # file is opened, now, json load it 
        pvjson = json.load(pvhandler)
        
        pvvanila = { "metadata": {"name": "p" + volumeid },
                     'spec': {'capacity': {'storage': pvsize },
                              'persistentVolumeReclaimPolicy': 'Recycle', 'accessModes': ['ReadWriteOnce'],
                              'awsElasticBlockStore': {'volumeID': volumeid , 'fsType': 'ext4'}}}
        pvjson.update(pvvanila)
        json.dump(pvjson, open("pvfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
        subprocess.call(["oc", "create", "-f", "pvfile.json"])
        os.remove("pvfile.json")

    # create persistent volume claim 
    def pclaim(self,pvcfile,pvcsize):

        self.pvcfile = pvcfile
        try:
            pvchandler = open(pvcfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file ... check input parameters")


        pvcjson = json.load(pvchandler)
        pvcvanila = {'metadata': {"name":"p" + volumeid },
                          'spec': {'accessModes': ['ReadWriteOnce'], 'resources': {'requests': {'storage': pvcsize }}}}
        pvcjson.update(pvcvanila)
        json.dump(pvcjson, open("pvcfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
        subprocess.call(["oc", "create", "-f", "pvcfile.json" ])
        os.remove("pvcfile.json")

    # create pod 
    def ppod(self,image,maxpod,minpod,podfile,mountpoint):

        global minpod 
        global maxpod 

        self.image = image 
        self.maxpod = maxpod 
        self.minpod = minpod 
        self.podfile = podfile
        self.mountpoint = mountpoint 

        try:
            podfile = open(self.podfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file ... check input parameters")

        podjson = json.load(podfile)
        podvanila = {'metadata': {'name': "pod" + str(minpod)},
                         'spec': {'containers': [{'image': image,
                                                  'imagePullPolicy': 'IfNotPresent',
                                                  'name': "pod" + str(minpod),
                                                  'volumeMounts': [{'name': 'p' + volumeid,
                                                  'mountPath': mountpoint }]}],
                                                  'volumes': [{'persistentVolumeClaim': {'claimName': "pclaim" + volumeid }, 'name': "p" + volumeid }]}}
        podjson.update(podvanila)
        json.dump(podjson,  open("podfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
        subprocess.call(["oc", "create", "-f", "podfile.json"])
        os.remove("podfile.json")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Script to create OSE pods and attach one EBS volume per pod as persistent storage")
    parser.add_argument("--volumesize", help="size of EBS voluems - in GB, for kubernetes correct it 5Gi, 300Mi... etc", default=5)
    parser.add_argument("--vtype", help="EBS volume type, default is gp2", default="gp2")
    parser.add_argument("--region", help="Amazon region where to connect", default="us-west-2b", required=True)
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
    parser.add_argument("--pvsize", help="persistent volume size - required parameter", required=True)
    parser.add_argument("--pvcsize", help="persistent volume claim size - required parameter", required=True)


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
    pvsize = args.pvsize 
    pvcsize = args.pvcsize 

    
    create_ebs = CreateEbs()
    total_pods = maxpod - minpod 
    while minpod < maxpod:
        create_ebs.ec2_volume(volumesize,vtype,region,tagprefix)
        create_ebs.pvolume(pvfile,pvsize)
        create_ebs.pclaim(pvcfile,pvcsize)
        create_ebs.ppod(image,maxpod,minpod,podfile,mountpoint)
        minpod = minpod + 1 
    
    print ( total_pods , "pods which use EBS as pessistent storage are created")


