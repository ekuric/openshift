#!/bin/bash 

MEMORY_LIMIT="$1"
TRANSACTIONS="$2"
STORAGECLASS="$3"
CLIENTS="$4"
ITERATIONS="$5"
THREADS="$6"
SCALING="$7"
NAMESPACE="$8"
TEMPLATE="$9"
VOLUME_CAPACITY="$10"
ITERATIONS="$11"
MODE="$12"
THREADS="$13"

for memory_limit in $(echo ${MEMORY_LIMIT} | sed -e s/,/" "/g); do
	for transactions in $(echo ${TRANSACTIONS} | sed -e s/,/" "/g); do
		pbench-user-benchmark --sysinfo=none --config=${STORAGECLASS}-podmem_${memory_limit}-trans${transactions}-clients${CLIENTS}-iter${ITERATIONS}-threads${THREADS}-scaling${SCALING} -- ./pgbench_test.sh -n ${NAMESPACE}-${transactions} -t ${transactions} -e ${TEMPLATE} -v ${VOLUME_CAPACITY} -m ${memory_limit} -i ${ITERATIONS} --mode ${MODE} --clients ${CLIENTS} --threads ${THREADS} --storageclass ${STORAGECLASS} --scaling ${SCALING}
	done 
done 

