#!/usr/bin/env bash

# script to run sysbench test inside pod - assumes sysbench and mariadb installed
# sysbench test run is oltp.lua - more information about
# oltp.lua find at : https://www.percona.com/docs/wiki/benchmark_sysbench_oltp.html


# defautls
NOK=1
# make dirs inside pod for mariadb
DB_DIR="/root/"
THREADS="1"
MARIADBCONF="/etc/my.cnf"
DATE=`date +%Y-%m-%d-%H-%M-%S`

##
usage() {
        printf  "Usage: ./$(basename $0) -d directory -t threads\n"
        printf -- "-d directory: directory which will be used by mariadb for read/write operations - this has to be provided otherwise /root/data and /root/datalog will be used\n"
        printf -- "-t threads : comma seperated list of values for number of threads, if none added, then default THREADS=1,6,12,24,48 is used\n"
        printf -- "-o oltp: number of rows in test table\n"
        printf -- "-r resultdir - the location where sybench results will be saved - this has to be mounted with -v (volume) option inside container"
        exit 0
}

if [ "$EUID" -ne 0 ] || [ "$#" -eq 0 ] ; then
    printf "Necessary to be root to run script and necessary to provide script parameters\n"
    printf "check options AND script has to be run on CEPH monitor - use carefully!\n"
    usage
    exit $NOK
fi

opts=$(getopt -q -o d:t:h:o:r: --longoptions "directory:,threads:,oltp:,resultdir:,help" -n "getopt.sh" -- "$@");
eval set -- "$opts";
echo "processing options"
while true; do
    case "$1" in
        -d|--directory)
            shift;
            if [ -n "$1" ]; then
                DB_DIR="$1"
                shift;
            fi
        ;;
        -t|--threads)
            shift;
            if [ -n "$1" ]; then
                THREADS="$1"
                shift;
            fi
        ;;
        -o|--oltp)
            shift;
            if [ -n "$1" ]; then
                oltp="$1"
                shift;
            fi
        ;;
        -r|--resultdir)
            shift;
            if [ -n "$1" ]; then
                resultdir="$1"
                shift;
            fi
        ;;
        -h|--help)
            usage
        ;;
        --)
            shift
            break;
        ;;
        *)
            shift;
            break;
    esac
done

# start mariadb

startdb() {

    # start database
    mkdir -p $DB_DIR/data
    mkdir -p $DB_DIR/datalog
    pkill mysqld_safe
    sed -i 's/pid\-file\=\/var\/run\/mariadb\/mariadb\.pid/pid\-file\=\/root\/mariadb\.pid/g' $MARIADBCONF
    echo "starting myslq..."
    mysqld_safe --user=root --basedir=/usr --skip-grant-tables --innodb_data_home_dir=$DB_DIR/data \
            --innodb_log_group_home_dir=$DB_DIR/datalog --innodb_log_buffer_size=64M \
            --innodb_thread_concurrency=0 --max_connections=1000 --table_cache=4096 --innodb_flush_method=O_DIRECT &

    sleep 120
}

prepare_db() {
    printf "Prepare sysbench environment and set up mariadb user\n"
    if [ ! -e /root/mariadb.pid ]; then
        sleep 5
    fi
    # todo: make mariadb more resilient
    sleep 120
    mysqladm -f -uroot -pmysqlpass drop sbtest
    mysqladmin -uroot -pmysqlpass create sbtest
    sysbench --test=/sysbench-0.5/sysbench/tests/db/oltp.lua --oltp-table-size=$oltp --mysql-db=sbtest --mysql-user=root --mysql-password=mysqlpass prepare
}

start_test() {
    printf "Runnint test for threads: $THREADS\n"
    for numthread in $(echo $THREADS | sed -e s/,/" "/g); do
        mkdir -p $resultdir/$(hostname -s)/threads_$numthread
        printf "Running test with $numthread sysbench threads\n"
        sysbench run --test=/sysbench-0.5/sysbench/tests/db/oltp.lua --num-threads=$numthread --mysql-table-engine=innodb --mysql-user=root --mysql-password=mysqlpass --oltp-table-size=$oltp --max-time=1800 --max-requests=100000 > $resultdir/$(hostname -s)/threads_$numthread/test_$DATE.log
        printf "Successfully finished sysbench test for $numthread sysbench threads\n"
    done
}

# main  - prepare and execute all
startdb
prepare_db
start_test





