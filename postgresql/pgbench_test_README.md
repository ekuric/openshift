### pgbench load tool for OCP pods 


pgbench_test.sh script can be used for executing pgbench benchmark tool
inside postgresql pod running inside OpenShift Container Platform (OCP) when 
cns storage backend is used for postgresql database backend 

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
		-m --mode what mode to run: file or blockprintf: usage: printf [-v var] format [arguments]

``` 

### Setup

pgbench_test.sh exepcts below to be in place and functioning before executing it 

- installed and properly setup pbench from [pbench](https://github.com/distributed-system-analysis/pbench)
- installed pgbench ( on centos/rhel it is part of postgresql-contrib package)
- template which supports dynamic storage provision 


pgbench_test.sh is expected to run as input script to pbench-user-benchmark

### Usage 

```
# pbench-user-benchmark --config="config_name" -- ./pgbench_test.sh -n <namespace> -t <transactions> -e <template> -v <vgsize> -m <memsize> -i <iterations> -m <mode> 
``` 
Where ```mode``` can be either ```block``` or ```file``` 


- for `block` case template needs to be configured to use storageclass based on cns block 
- for `file` case template requirement for template is to use storageclass based on cns file 

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



Example usage of ```pgbench_test.sh``` 


``` 
# pbench-user-benchmark --config="test_postgresql" -- ./pgbench_test.sh -n pgblock -t 100 -e glusterblock-postgresql-persistent -v 20 -m 2 -i 5 --mode file 
``` 


