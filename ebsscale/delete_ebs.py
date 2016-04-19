#!/usr/bin/env python

import boto3
import argparse
import botocore
import time
import subprocess
import logging
import json 

def main():
    parser = argparse.ArgumentParser(description="Script to delete EBS volume - based on tag it has")
    parser.add_argument("--tagname", help="tagname which is used by EBS volume", required=True)

    args = parser.parse_args()
    tagname = args.tagname

    ec2 = boto3.resource("ec2")
    def delete_ebs():

        global tagname
	logging.basicConfig(filename='delete.log',level=logging.INFO, format='%(message)s')  # , format='%(asctime)s %(message)s')
        tagname = args.tagname


	#ebs_logger = logging
	formatter = logging.Formatter('%(message)s')

	# ebs logger
	ebs_logger = logging.getLogger('ebslogger')
	ebsdelhand = logging.FileHandler('ebsdelete.log')
	ebsdelhand.setFormatter(formatter)
	ebs_logger.addHandler(ebsdelhand)
	
	# pv  logger
	pv_logger = logging.getLogger('pvlogger')
	pvhand = logging.FileHandler('pvdelete.log')    
	pvhand.setFormatter(formatter)
	pv_logger.addHandler(pvhand)

	# pvc logger
	pvc_logger = logging.getLogger('pvclogger')
	pvchand = logging.FileHandler('pvcdelete.log')
	pvchand.setFormatter(formatter)
	pvc_logger.addHandler(pvchand)
	
	while True:
		try:
           		volumestag = ec2.volumes.filter(Filters=[{'Name' : 'tag-value', 'Values':[tagname]}])
            		# for keys it would be ec2.volumes.filter(Filters=[{'Name' : 'tag-key', 'Values':[tagkey]}])
            		for volume in volumestag:
	                	start_delete = time.time()
        	        	volume.delete(DryRun=False)
                		end_delete = time.time() 
				ebs_logger.info('%s, %s, %s',"ebs_volume deleted", volume.id,end_delete - start_delete)
				pvstart = time.time()
		                subprocess.call(["oc", "delete", "pv" , "p"+volume.id+"-"+"pvolume"])
		    		pvend = time.time()
				pv_logger.info('%s, %s,%s',"pv_volume deleted" ,"p"+volume.id+"-"+"pvolume",  pvend - pvstart)
 		                subprocess.call(["oc", "delete", "pvc", "pclaim"+volume.id])
 				pvcend = time.time()
 				pvc_logger.info('%s, %s, %s' ,"pvc_claim deleted", "pclaim"+volume.id, pvcend - pvend)
        	except botocore.exceptions.ClientError as err:
			print ("excepsion happended...we have errror ... ", err.response['Error']['Code'])
			continue 
                
		else:
			print ("volume deleted")
		break 
    delete_ebs()


if __name__ == '__main__':
    main()
