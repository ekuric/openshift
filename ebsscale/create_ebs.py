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
import sys
import botocore
import logging

class CreateEbs():

    def __init__(self):
	
        # create EC2 connector 
	print ("Class to create EBS")

    def ec2_volume(self,volumesize,vtype,region,tagprefix,num):

        self.volumesize = volumesize
        self.vtype = vtype  
        self.region = region
        self.tagprefix = tagprefix
	self.num = num 

	logging.basicConfig(filename='create.log',level=logging.INFO, format='%(message)s')  # , format='%(asctime)s %(message)s')


	formatter = logging.Formatter('%(message)s')

	# ebs logger create 
	ebs_logger = logging.getLogger('ebslogger')
	ebsh = logging.FileHandler('ebscreate.log')
	ebsh.setFormatter(formatter)
	ebs_logger.addHandler(ebsh)

	# ebs logger tag 
	ebs_logger_tag = logging.getLogger('ebstaglogger')
	hdlr_tag = logging.FileHandler('ebstag.log')
	hdlr_tag.setFormatter(formatter)
	ebs_logger_tag.addHandler(hdlr_tag)

	# pv  logger
	global pv_logger
	pv_logger = logging.getLogger('pvlogger')
	pvhand = logging.FileHandler('pvcreate.log')    
	pvhand.setFormatter(formatter)
	pv_logger.addHandler(pvhand)

	# pvc logger
	global pvc_logger
	pvc_logger = logging.getLogger('pvclogger')
	pvchand = logging.FileHandler('pvccreate.log')
	pvchand.setFormatter(formatter)
	pvc_logger.addHandler(pvchand)
	
	global tags
        global volumeid 
	while True:
		try:
			ec2 = boto3.resource("ec2")
        		vc_start = time.time() 
        		volume = ec2.create_volume(VolumeType=vtype,
                                       AvailabilityZone=region,
                                       Size=volumesize)
        		vc_stop = time.time()
        		volumeid = volume.id
			ebs_logger.info('%s, %s, %s',"ebs_volume_created", volume.id,vc_stop - vc_start)
		except botocore.exceptions.ClientError as err:
			# if this exception happens... we do not care ... volume will not be created and that is .... 
			continue
		try:
			tag_start = time.time()
			tags = ec2.create_tags(DryRun=False, Resources=[volumeid],Tags=[{'Key': tagprefix + volumeid, 'Value': tagprefix},])
			tag_end = time.time()
			ebs_logger_tag.info('%s, %s, %s', "ebs_volume_tagged", volume.id, tag_end - tag_start)

		except botocore.exceptions.ClientError as err:
			print ("exception happended in tagging block ... we will sleep 5 sec ...and try again to tag it again", err.response['Error']['Code'])
			time.sleep(5)
			continue
			try:
				tags = ec2.create_tags(DryRun=False, Resources=[volumeid],Tags=[{'Key': tagprefix + volumeid, 'Value': tagprefix},])
			except botocore.exceptions.ClientError as err:
				print ("nottagging volume", volumeid)
		else:
			print ("volume", volumeid, "tagged in ", tag_end - tag_start) 
		break
    # create persistent volume 
    def pvolume(self,pvfile,pvsize,num):

        self.pvfile = pvfile
	self.pvsize = pvsize
	self.num = num 

        try:
            pvhandler = open(pvfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file... check input parameters")

        # file is opened, now, json load it 
        pvjson = json.load(pvhandler)
        
        pvvanila = { "metadata": {"name": "p" + volumeid + "-"+"pvolume" },
                     'spec': {'capacity': {'storage': pvsize + "Gi" },
                              'persistentVolumeReclaimPolicy': 'Recycle', 'accessModes': ['ReadWriteOnce'],
                              'awsElasticBlockStore': {'volumeID': volumeid , 'fsType': 'ext4'}}}
        pvjson.update(pvvanila)
        json.dump(pvjson, open("pvfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
	pvstart=time.time()
        subprocess.call(["oc", "create", "-f", "pvfile.json"])
	pvend=time.time()
	pv_logger.info('%s, %s, %s',"pv_volume_created", "p"+volumeid+"-"+"pvolume",pvend - pvstart)

    # create persistent volume claim 
    def pclaim(self,pvcfile,pvcsize,num):

        self.pvcfile = pvcfile
	self.pvcfize = pvcsize 
	self.num = num 
        try:
            pvchandler = open(pvcfile,"r")
        except FileNotFoundError:
            print ("Not possible to find file ... check input parameters")


        pvcjson = json.load(pvchandler)
        pvcvanila = {'metadata': {"name":"pclaim" + volumeid },
                          'spec': {'accessModes': ['ReadWriteOnce'], 'resources': {'requests': {'storage': pvcsize + "Gi" }}}}
        pvcjson.update(pvcvanila)
        json.dump(pvcjson, open("pvcfile.json", "w+"),sort_keys=True, indent=4, separators=(',', ': '))
	pvcstart=time.time()
        subprocess.call(["oc", "create", "-f", "pvcfile.json" ])
	pvcend=time.time()
	pvc_logger.info('%s, %s, %s',"pvc_claim_created", "pclaim" + volumeid, pvcend - pvcstart)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Script to create OSE pods and attach one EBS volume per pod as persistent storage")
    parser.add_argument("--volumesize", help="size of EBS voluems - in GB ", default=5, type=int)
    parser.add_argument("--vtype", help="EBS volume type, default is gp2", default="gp2")
    parser.add_argument("--region", help="Amazon region where to connect", default="us-west-2b")
    parser.add_argument("--tagprefix", help="tag prefix for EBS volumes, default tag is openshift-testing-EBS_volume_id", default="openshift-testing")

    # required arguments
    parser.add_argument("--pvfile", help="persistent volume definition json file - required parameter", required=True)
    parser.add_argument("--pvcfile", help="persistent volume claim definition json file - required parameter", required=True)
    parser.add_argument("--pvsize", help="pv size", required=True)
    parser.add_argument("--pvcsize", help="pvc size",required=True)
    parser.add_argument("--num", help="how many pods", required=True)

    args = parser.parse_args()

    volumesize = args.volumesize
    vtype = args.vtype
    region = args.region
    tagprefix = args.tagprefix
    pvfile = args.pvfile
    pvcfile = args.pvcfile
    pvsize = args.pvsize	
    pvcsize = args.pvcsize 
    num = args.num 
    create_ebs = CreateEbs()
    for num in range(0,int(num)):
        create_ebs.ec2_volume(volumesize,vtype,region,tagprefix,num)
        create_ebs.pvolume(pvfile,pvsize,num)
        create_ebs.pclaim(pvcfile,pvcsize,num)
