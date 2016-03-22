#!/usr/bin/env bash

# script to delete pods/pv/pvc and EBS volumes
podtag="$1"
pvtag="$2"
pvctag="$3"
ebstag="$4"

# delete pods
if [ -n "$podtag" ]; then
	for pod in $(oc get pods | grep "$podtag*" | awk '{print $1}'); do
    	oc delete pod --grace-period=0 $pod
	done
elif [[ -z "$podtag" ]]; then
	for pod in $(oc get pods | grep ^pod | awk '{print $1}'); do
		oc delete pod --grace-period=0 $pod
	done
else
	printf "Something is broken... check options\n"
fi 


printf "Sleeping 60 sec to allow AWS to detach EBS volume from instance\n"
printf "otherwise EBS delete will fail - not possible to remove EBS used by aws instance\n"

sleep 60

# delete pv

if [ -n "$pvtag" ]; then 
	for pvolume in $(oc get pv | grep "$pvtag*" | awk '{print $1}'); do
    	oc delete pv --grace-period=0 $pvolume
	done
elif [[ -z "$pvtag" ]]; then
	for pvolume in $(oc get pv | grep pvolume | awk '{print $1}'); do
		oc delete pv --grace-period=0 $pvolume
	done 
else
	printf "Something is broken, check options\n"
fi 



# delete pvc

if [ -n "$pvctag" ]; then 
	for pvclaim in $(oc get pvc | grep "$pvctag*" | awk '{print $1}'); do
    	oc delete pvc --grace-period=0 $pvclaim
	done
elif [[ -z "$pvctag" ]]; then
	for pvclaim in $(oc get pvc | grep pvclaim | awk '{print $1}'); do
		oc delete pvc --grace-period=0 $pvclaim
	done 
else
	printf "Something is broken ... check options\n"
fi 


# delete ebs

if [ -n "$ebstag" ]; then
	for ebs in $(aws ec2 describe-volumes --filter Name=tag-value,Values="$ebstag*" --query 'Volumes[*].{ID:VolumeId}' --output text); do
    	printf "Deleting EBS volume::" ; echo $ebs
    	aws ec2 delete-volume --volume-id $ebs
	done
else
	# do not run delete EBS step if EBS tag is not provided 
	printf "EBS tag not in input paraemters... we exit here, specify EBS tag and rerun this script\n"
	exit 0 
fi 