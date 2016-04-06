#!/usr/bin/env bash

# script to run sysbench test inside pod - assumes sysbench and mariadb installed

# defautls
NOK=1
# make dirs inside pod for mariadb
DB_DIR="/root/"
THREADS="1,6,12,24,48"
MARIADBCONF="/etc/my.cnf"

##
usage() {
        printf  "Usage: ./$(basename $0) -d directory -t threads\n"
        printf -- "-d directory: directory which will be used by mariadb for read/write operations - this has to be provided otherwise /root/data and /root/datalog will be used\n"
        printf -- "-t threads : comma seperated list of values for number of threads, if none added, then default THREADS=1,6,12,24,48 is used\n"
        exit 0
}

if [ "$EUID" -ne 0 ] || [ "$#" -eq 0 ] ; then
    printf "Necessary to be root to run script and necessary to provide script parameters\n"
    printf "check options AND script has to be run on CEPH monitor - use carefully!\n"
    usage
    exit $NOK
fi

opts=$(getopt -q -o d:t:h --longoptions "directory:,threads:,help" -n "getopt.sh" -- "$@");
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
    mysqld_safe --user=root --basedir=/usr --skip-grant-tables --innodb_data_home_dir=$DB_DIR/data \
            --innodb_buffer_pool_size=2048M --innodb_log_group_home_dir=$DB_DIR/datalog --innodb_log_buffer_size=64M \
            --innodb_additional_mem_pool_size=32M --innodb_flush_log_at_trx_commit=0 --innodb_log_file_size=1G \
            --innodb_thread_concurrency=1000 --max_connections=1000 --table_cache=4096 --innodb_flush_method=O_DIRECT &
}

configure_sysbench() {
    cd /root/perf-dept/bench/sysbench
    unzip 0.5.zip && cd sysbench-0.5  && ./autogen.sh && ./configure && make && make install
    printf "sysbench 0.5 is installed and in place ...ready to run test  \n"
}


prepare_db() {
    printf "Prepare sysbench environment and set up mariadb user\n"
    if [ ! -e /root/mariadb.pid ]; then
        sleep 5
    fi
    sleep 25
    mysqladmin -f -uroot -pdbpassword drop sbtest
    mysqladmin -uroot -pdbpassword create sbtest
    sysbench --test=/root/perf-dept/bench/sysbench/sysbench-0.5/sysbench/tests/db/oltp.lua --oltp-table-size=50000000 --mysql-db=sbtest --mysql-user=root --mysql-password=dbpassword prepare
}

start_test() {
    printf "Runnint test for threads $THREADS  - if not specified with -t - this is default\n"
    mkdir -p /var/lib/pbench-agent/$(hostname -s)
    for numthread in $(echo $THREADS | sed -e s/,/" "/g); do
        printf "Running test with $numthread sysbench threads\n"
        sysbench run --test=/root/perf-dept/bench/sysbench/sysbench-0.5/sysbench/tests/db/oltp.lua --num-threads=$numthread --mysql-table-engine=innodb \
        --mysql-user=root --mysql-password=dbpassword --oltp-table-size=10000000 --max-time=1800 --max-requests=10000000 > /var/lib/pbench-agent/$(hostname -s)/test_4GBP_thread_$numthread.log
        printf "Successfully finished sysbench test for $numthread sysbench threads\n"
    done
}

# main  - prepare and execute all

startdb
# configure_sysbench - disabled at time, configured during docker image build
prepare_db
start_test





