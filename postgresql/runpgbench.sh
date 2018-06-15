#!/bin/bash 

NAMESPACE="${1}"
TRANSACTIONS="${2}"
TEMPLATE="${3}"
VOLUME_CAPACITY="${4}"
MEMORY_LIMIT="${5}"
ITERATIONS="${6}"
MODE="${7}"
CLIENTS="${8}"
THREADS="${9}"
SCALING="${10}"
STORAGECLASS="${11}"
PBENCHCONFIG="${12}"
PBENCHS="${13}"

for memory_limit in $(echo ${MEMORY_LIMIT} | sed -e s/,/" "/g); do
	for transactions in $(echo ${TRANSACTIONS} | sed -e s/,/" "/g); do
		if [[ "$PBENCHS" == "pbenchs" ]] ; then
			pbench-user-benchmark --sysinfo=none -C "pgbench_${STORAGECLASS}-podmem_${memory_limit}-trans${transactions}-clients${CLIENTS}-iter${ITERATIONS}-threads${THREADS}-scaling${SCALING}" \
			--pbench-post='/usr/local/bin/pbscraper -i $benchmark_results_dir/tools-default -o $benchmark_results_dir; ansible-playbook -vv -i /root/svt/utils/pbwedge/hosts /root/svt/utils/pbwedge/main.yml -e new_file=$benchmark_results_dir/out.json -e git_test_branch='${STORAGECLASS}-podmem_${memory_limit}-trans${transactions}-clients${CLIENTS}-iter${ITERATIONS}-threads${THREADS}-scaling${SCALING} \
			-- ./pgbench_test.sh -n ${NAMESPACE}-${transactions} -t ${transactions} -e ${TEMPLATE} -v ${VOLUME_CAPACITY} -m ${memory_limit} -i ${ITERATIONS} --mode ${MODE} --clients ${CLIENTS} --threads ${THREADS} --storageclass ${STORAGECLASS} --scaling ${SCALING}
		else
			pbench-user-benchmark --sysinfo=none -C "pgbench_${STORAGECLASS}-podmem_${memory_limit}-trans${transactions}-clients${CLIENTS}-iter${ITERATIONS}-threads${THREADS}-scaling${SCALING}" -- ./pgbench_test.sh -n ${NAMESPACE}-${transactions} \
			-t ${transactions} -e ${TEMPLATE} -v ${VOLUME_CAPACITY} -m ${memory_limit} -i ${ITERATIONS} --mode ${MODE} \
			--clients ${CLIENTS} --threads ${THREADS} --storageclass ${STORAGECLASS} --scaling ${SCALING}
		fi 

	done 
done 

