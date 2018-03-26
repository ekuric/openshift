### pgbench load tool for OCP pods 


[pgbench_test.sh](https://github.com/ekuric/openshift/blob/master/postgresql/pgbench_test.sh) script can be used for executing pgbench benchmark tool
inside postgresql pod running on top of Kubernetes / OpenShift Container Platform (OCP) when CNS ( Container Native Storage )
is used as storage backend for Postgresql pod


### Supported options 

pgbench_test.sh supports below options 

``` 
The following options are available:

		-n str --namespace=str name for new namespace to create pod inside
		-t str[,str] --transactions=str[,str] the number pgbench transactions
		-e str[,str] --template=str[,str what template to use
		-v --volsize the size of volume for database
		-m --memsize the size of memory to assign to postgresql pod
		-i --iterations how many iterations of test to execute
		-m --mode what mode to run: ```cnsfile```, ```cnsblock```, or ```otherstorage```
		-r --resultdir name of directory where to place pgbench results

``` 

### Setup

pgbench_test.sh exepcts below to be in place and functioning before executing it 

- pgbench_test.sh can be executed as standalone script 

In case there is need to run it as user script for [pbench](https://github.com/distributed-system-analysis/pbench)
then below must be satisfied prior executing it 

- installed and properly setup pbench from [pbench](https://github.com/distributed-system-analysis/pbench)
- installed pgbench ( on centos/rhel it is part of `postgresql-contrib package`)
- template which supports dynamic storage provision using storage classes 


pgbench_test.sh is can be used to run as input script to pbench-user-benchmark
pgbench_test.sh can be used as standalone script 

### Usage:  

- standalone case 

```
./pgbench_test.sh -n <namespace> -t <transactions> -e <template> -v <vgsize> -m <memsize> -i <iterations> --mode <mode> -r resultdir 
```
- as input script for pbench-user-benchmark 

```
# pbench-user-benchmark --config="config_name" -- ./pgbench_test.sh -n <namespace> -t <transactions> -e <template> -v <vgsize> -m <memsize> -i <iterations> --mode <mode> 
``` 
Where ```mode``` can be either ```cnsblock```, ```cnsfile```, or ```otherstorage```  


- for `cnsblock` case template needs to be configured to use storageclass based on cns block 
- for `cnsfile` case template requirement for template is to use storageclass based on cns file 
- as it can be clear from name, ```otherstorage``` means any other storage configured in storage class section inside template used for postgresql 

Example how to edit PVclaim section in template is showed below 

``` 
        ...
        ....
		"annotations":
			"volume.beta.kubernetes.io/storage-class": "glusterblock"
                "name": "${DATABASE_SERVICE_NAME}"
            },
            .... 
            ....
``` 



``` 
# pbench-user-benchmark --config="test_postgresql" -- ./pgbench_test.sh -n pgblock -t 100 -e glusterblock-postgresql-persistent -v 20 -m 2 -i 5 --mode cnsfile 
``` 

### Todo 

Get support for ```kubectl``` client to be k8s compatible (PR welcome)
