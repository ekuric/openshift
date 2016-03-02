# program to create Amazon EC2 volumes

import argparse
import boto3
import subprocess
import os
import json
import sys

def main():

    # parse arguments
    parser = argparse.ArgumentParser(description="Script to create Amazon EBS volumes")
    parser.add_argument("--vnumber", help="Number of EBS volume to create", default=1, type=int)
    parser.add_argument("--volumesize", help="size of EBS voluems - in GB ", default=5, type=int)
    parser.add_argument("--vtype", help="volume type", default="gp2")
    parser.add_argument("--region", help="Amazon region where to connect", default="us-west-2b")
    parser.add_argument("--image", help="docker image to use", default="r7perffio")
    parser.add_argument("--pnumber", help="number of pods", default=1, type=int)
    parser.add_argument("--tagprefix", help="tag prefix - something to differ tags", default="openshift-testing")
    parser.add_argument("--mountpoint", help="mount point inside pod where volume will be mounted", default="/mnt/persistentvolume")
    parser.add_argument("--snumber", help="start value from which pods will be created, default is 0, - pod0, pod1, ... pnumber will be created", type=int, default=0)

    # required arguments
    parser.add_argument("--enumber", help="end value for number of pods", type=int, required=True)
    parser.add_argument("--pvfile", help="persistent volume definition json file", required=True)
    parser.add_argument("--pvcfile", help="persistent volume claim definition json file", required=True)
    parser.add_argument("--podfile", help="pod definition json file", required=True)


    args = parser.parse_args()

    vnumber  =  args.vnumber
    pnumber = args.pnumber
    volumesize = args.volumesize
    vtype = args.vtype
    region = args.region
    tagprefix = args.tagprefix
    mountpoint = args.mountpoint
    image = args.image
    pvfile = args.pvfile
    pvcfile = args.pvcfile
    podfile = args.podfile
    snumber = args.snumber
    enumber = args.enumber

    session = boto3.Session(region_name=region)
    ec2 = boto3.resource("ec2")

    def create_ebs_pod():

        global snumber
        snumber = args.snumber

        while snumber < enumber:

            volume = ec2.create_volume(VolumeType=vtype,
                                       AvailabilityZone=region,
                                       Size=volumesize)

            # volume created ... tag it for easier finding later - based on this tag
            tags = ec2.create_tags(DryRun=False, Resources=[volume.id],
                                   Tags=[
                                       {'Key': tagprefix + volume.id,
                                        'Value': tagprefix + volume.id
                                        },
                                   ])

            # create pv ( add here try/except/finaly stuff - same for pvc / pod stanza
            try:
                pvhandler = open(pvfile,"r")
            except IOError:
                    print ("Cannot open file persistent volume file, is it specified?")

            pvdoc = json.load(pvhandler)
            pvvanila = { "metadata": {"name": "pvolume" + str(snumber) },
                       'spec': {'capacity': {'storage': volumesize },
                        'persistentVolumeReclaimPolicy': 'Recycle', 'accessModes': ['ReadWriteOnce'],
                        'awsElasticBlockStore': {'volumeID': volume.id , 'fsType': 'ext4'}}}

            pvdoc.update(pvvanila)
            json.dump(pvdoc, open("pvfile.json","w+"))
            # run an create now pv
            subprocess.call(["oc", "create", "-f", "pvfile.json"])
            os.remove("pvfile.json")

            # todo  - implement to check does PV/PVC/POD already exist on system
            # create pvc
            try:
                pvchandler = open(pvcfile,"r")
            except IOError:
                print ("Cannot open persistent volume claim file, is it specified?")

            pvcdoc = json.load(pvchandler)
            pvcvanila = {'metadata': {"name":"pvclaim" + str(snumber)},
                          'spec': {'accessModes': ['ReadWriteOnce'], 'resources': {'requests': {'storage': volumesize }}}}

            pvcdoc.update(pvcvanila)
            json.dump(pvcdoc, open("pvcfile.json", "w+"))
            subprocess.call(["oc", "create", "-f", "pvcfile.json"])
            os.remove("pvcfile.json")
            # create pod

            try:
                podhandler = open(podfile, "r")
            except IOError:
                print ("Cannot open pod file, is it specified? Check options")

            poddoc = json.load(podhandler)
            podvanila = {'metadata': {'name': "pod" + str(snumber)},
                         'spec': {'containers': [{'image': image,
                                                  'imagePullPolicy': 'IfNotPresent',
                                                  'name': "pod" + str(snumber),
                                                  'volumeMounts': [{'name': 'pvolume' + str(snumber),
                                                  'mountPath': mountpoint }]}],
                                                  'volumes': [{'persistentVolumeClaim': {'claimName': "pvclaim" + str(snumber)}, 'name': "pvolume" + str(snumber)}]}}
            poddoc.update(podvanila)
            json.dump(poddoc, open("podfile.json", "w+"))
            subprocess.call(["oc", "create", "-f", "podfile.json"])
            os.remove("podfile.json")
            subprocess.call(["oc", "get", "pods"])

            snumber = snumber + 1

    create_ebs_pod()


if __name__ == '__main__':
    main()

