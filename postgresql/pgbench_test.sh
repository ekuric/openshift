#!/bin/bash 

# Script to to run pgbench load test against postgresql pod in kubernetes/Openshift
  

opts=$(getopt -q -o n:t:e:v:m:i: --longoptions "namespace:,transactions:,template:,volsize:,memsize:,iterations:,mode:" -n "getopt.sh" -- "$@");

if [ $? -ne 0 ]; then
    printf -- "$*\n"
    printf "\n"
    printf "You specified an invalid option\n"
    printf "\tThe following options are available:\n\n"
    printf -- "\t\t-n str --namespace=str name for new namespace to create pod inside\n"
    printf -- "\t\t-t str[,str] --transactions=str[,str] the number pgbench transactions\n"
    printf -- "\t\t-e str[,str] --template=str[,str what template to use\n"
    printf -- "\t\t-v --volsize the size of volume for database\n"
    printf -- "\t\t-m --memsize the size of memory to assign to postgresql pod\n"
    printf -- "\t\t-i --iterations how many iterations of test to execute\n"
    printf -- "\t\t-m --mode what mode to run: file or block"
    printf 
    exit 1 
fi

eval set -- "$opts";
echo "processing options" 

while true; do
    case "$1" in
        -n|--namespace)
            shift;
            if [ -n "$1" ]; then
                namespace="$1"
                shift;
            fi
        ;;
        -t|--transactions)
            shift;
            if [ -n "$1" ]; then 
                transactions="$1"
                shift;
            fi 
        ;; 
        -e|--template)
            shift;
            if [ -n "$1" ]; then 
                template="$1"
                shift;
            fi
        ;; 
        -v|--volsize)
            shift;
            if [ -n "$1" ]; then 
                volsize="$1"
                shift;
            fi
        ;;
        -m|--memsize)
            shift;
            if [ -n "$1" ]; then 
                memsize="$1"
                shift;
            fi
        ;;
        -i|--iterations)
            shift;
            if [ -n "$1" ]; then 
                iterations="$1"
                shift;
            fi
        ;;
        --mode)
            shift; 
            if [ -n "$1" ]; then 
                mode="$1"
                shift
            fi
        ;;
        --)
            break;
        ;;
        *)
            printf "Check options... something is not good\n"
        ;;
    
    esac 
done 

function create_pod {
        oc new-project $namespace 
        oc new-app --template=$template -p VOLUME_CAPACITY=${volsize}Gi -p MEMORY_LIMIT=${memsize}Gi
        while [ "$(oc get pods | grep -v deploy | awk '{print $3}' | grep -v STATUS)" != "Running" ] ; do 
	        printf "sleeping 5s, waiting postgresql pod to fully start"
	        sleep 5
        done 
        printf "postgresql is started - waiting 30s before proceed"
        sleep 30 
} 

function run_test { 
        POD=$(oc get pods | grep postgresql | grep -v deploy | awk '{print $1}')
        SERVICE=$(oc exec $POD -- env | grep -i ^POSTGRESQL_SERVICE_HOST | cut -d'=' -f2)
        USER=$(oc exec $POD -- env | grep -i POSTGRESQL_USER | cut -d'=' -f2)
        PASS=$(oc exec $POD -- env | grep -i POSTGRESQL_PASSWORD | cut -d'=' -f2)
        # This is temporarly hack before find better mode to manage passwrds 
        # do not want to be prompted for password 
        echo "$SERVICE:5432:*:$USER:$PASS" >> /root/.pgpass
        printf "Running test preparation\n" 
        pgbench -h $SERVICE -p 5432  -i -s $transactions sampledb -U $USER

    # run x itterations of test 
        for m in $(seq 1 $iterations); do 
	        pgbench -h $SERVICE -p 5432  -c 10 -j 2 -t $transactions sampledb -U $USER >> $benchmark_run_dir/pgbench_run_$m.txt 
	        grep "excluding connections establishing" $benchmark_run_dir/pgbench_run_$m.txt | cut -d'=' -f2 |cut -d' ' -f2  >> $benchmark_run_dir/excluding_connection_establishing.txt 
	        grep "including connections establishing" $benchmark_run_dir/pgbench_run_$m.txt | cut -d'=' -f2 |cut -d' ' -f2 >> $benchmark_run_dir/including_connections_establishing.txt 
        done 
} 

function volume_setup {
    
    CNSPOJECT=$(oc get pods --all-namespaces  | grep glusterfs-storage | awk '{print $1}'  | head -1)
    CNSPOD=$(oc get pods --all-namespaces  | grep glusterfs-storage | awk '{print $2}'  | head -1)
    PV=$(oc get pvc | grep Bound | awk '{print $3}')
    GLUSTERVOLUME=$(oc describe pv $PV | grep vol_  | awk '{print $2}')

    oc exec -n $CNSPOJECT $CNSPOD -- gluster volume set $GLUSTERVOLUME performance.stat-prefetch off
    oc exec -n $CNSPOJECT $CNSPOD -- gluster volume set $GLUSTERVOLUME performance.write-behind off
    oc exec -n $CNSPOJECT $CNSPOD -- gluster volume set $GLUSTERVOLUME performance.strict-o-direct on 
    oc exec -n $CNSPOJECT $CNSPOD -- gluster volume set $GLUSTERVOLUME performance.read-ahead off 
    oc exec -n $CNSPOJECT $CNSPOD -- gluster volume set $GLUSTERVOLUME performance.io-cache off 
    oc exec -n $CNSPOJECT $CNSPOD -- gluster volume set $GLUSTERVOLUME performance.readdir-ahead  off
   
    # add more options here - make it parameters 
}

# necessary to polish this ... 
case $mode in
    block)
	    create_pod
        run_test 	
    ;;
    file)
	    create_pod
        volume_setup
	    run_test
    ;;
esac 
