- pgbench_test.sh script can be used for executing pgbench inside postgresql pod
running inside OpenShift Container Platform (OCP)

pgbench_test.sh is expected to run as input script to pbench-user-benchmark

usage: 

pbench-user-benchmark --config="test_postgresql" -- ./pgbench_test.sh  <namespace> <transactions> <template> <vgsize> <memsize> <iterations> 

eg: 

pbench-user-benchmark --config="test_postgresql" -- pgblock 8000 glusterblock-postgresql-persistent 200 15 10 

