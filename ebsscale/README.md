## Usage 

### Create EBS/PV/PVC 

`# python create_ebs_pod.py --volumesize=1 --vtype=gp2  --tagprefix=my_test --pvfile=pv.json --pvcfile=pvc.json --num=1 --pvsize=1 --pvcsize=1`

This will create 1 EBS/PV/PVC of size 1 GB, type gp2, tagged with tag `my_test` 

### delete EBS/PV/PVC

`python delete_ebs.py --tagname=my_test`

This will delete all EBS with tag `my_test`

These scripts requires 

- proper setup of OSE nodes in sense of AWS - keys/credentials and Openshift node/Openshift master configuration has to 
be properly configured in advance 


