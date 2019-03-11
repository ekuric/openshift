#!/bin/bash

testproject=$1
cephpool=$2

output_dir=$(dirname $0)

if [[ ! -z "${benchmark_results_dir}" ]]; then
  output_dir="${benchmark_results_dir}"
fi

tools_pod=$(oc get pods -n rook-ceph |grep rook-ceph-tools |awk '{print $1}') 

# delete all stuff there 
oc delete pods -n $testproject --all --wait=false 
oc delete pvc -n $testproject  --all --wait=false

while [[ $(oc exec -n rook-ceph $tools_pod -- rbd ls $cephpool |wc -l) -gt 0 ]]; do 
        oc exec -n rook-ceph $tools_pod -- rbd ls $cephpool |wc -l >> $output_dir/number_of_rbd_devices.csv
	      echo "waiting on RBD to be deleted"
	      sleep 1
done 

echo "all rbds are removed ...."
echo "number of rbds is:" 
oc exec -n rook-ceph $tools_pod -- rbd ls $cephpool |wc -l
sleep 30
echo "Test finished"


