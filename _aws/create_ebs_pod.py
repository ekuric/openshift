# program to create Amazon EC2 volumes
__author__ = "elko"

import argparse
import boto3
import subprocess
import os
import json

def main():

    # optional arguments
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
    tagprefix = args.tagprefix
    mountpoint = args.mountpoint
    image = args.image
    pvfile = args.pvfile
    pvcfile = args.pvcfile
    podfile = args.podfile
    minpod = args.minpod
    maxpod = args.maxpod
    action = args.action

    session = boto3.Session(region_name=region)
    ec2 = boto3.resource("ec2")

    def create_ebs_pod():
        """
        create_ebs_pod() function will do
        - create EBS volume
        - tag EBS volume
        - create PV/PVC
        - crete pod and attach already created EBS volume to POD as persistent storage
        """
        global minpod
        minpod = args.minpod

        while minpod < maxpod:

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
            pvvanila = { "metadata": {"name": "pvolume" + str(minpod) },
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
            pvcvanila = {'metadata': {"name":"pvclaim" + str(minpod)},
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
            podvanila = {'metadata': {'name': "pod" + str(minpod)},
                         'spec': {'containers': [{'image': image,
                                                  'imagePullPolicy': 'IfNotPresent',
                                                  'name': "pod" + str(minpod),
                                                  'volumeMounts': [{'name': 'pvolume' + str(minpod),
                                                  'mountPath': mountpoint }]}],
                                                  'volumes': [{'persistentVolumeClaim': {'claimName': "pvclaim" + str(minpod)}, 'name': "pvolume" + str(minpod)}]}}
            poddoc.update(podvanila)
            json.dump(poddoc, open("podfile.json", "w+"))
            subprocess.call(["oc", "create", "-f", "podfile.json"])
            os.remove("podfile.json")

            minpod = minpod + 1

    create_ebs_pod()

if __name__ == '__main__':
    main()


