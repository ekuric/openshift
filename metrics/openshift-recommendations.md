## Openshift Metrics sizing guidlines [ draft ]

### Openshift Metrics basics

Monitoring openshift pods is important task from Openshift adminsitrator and Openshift user point
of view. Openshift administrators need a way to monitor pods of interest and see how they perform and react if necessary
to fix critical issue, and at other side Openshift users also need simple and comprehensive overview of pods where their
application runs.

This guide will provide basic Openshift metrics guidlines Openshift administrators and users can
follow when trying to dimension metrics system for openshift installations

### Openshift Metrics installation

Installation of Openshift metrics is described in [Openshift upstream origin metrics documentation](https://github.com/openshift/origin-metrics )
and for Openshift Enterprise [Openshift Enterprise v3 documentation](https://docs.openshift.com/enterprise/3.2/install_config/cluster_metrics.html)
For instruction how to configure Opensift metrics on Openshift cluster, please follow instruction
in these two links.

However, it is very important to fulfill below points when starting Opensift metrics in order to avoid potential issues which can
appear in later phase


- use `persistant_storage=true` parameter. Persistent storage parameter is necessary if we want metrics
data to persist across metrics pods lifetime. Prior using `persistant_storage=true` it is necessaary to have have available
peristant volume. Please check [Openshift Enterprise documentation - how to create persistant volume](https://docs.openshift.com/enterprise/3.2/dev_guide/persistent_volumes.html)
for detailed instructions.
Openshift metrics supports also [dynamically provisioned](https://github.com/openshift/origin-metrics/blob/master/metrics.yaml#L130)
Persistent Volumes ( PV ) and to use this feature Openshift metrics need to be started with
`DYNAMICALLY_PROVISION_STORAGE=true`
parameter. At time only EBS, GCE and Cinder storage backends can be used to dynamically
provision persistent volumes for Openshift. For more inforamtion related to dynamicly provisioned PV, check
[Openshift documentation](https://docs.openshift.com/enterprise/3.2/install_config/persistent_storage/dynamically_provisioning_pvs.html)

If ```persistent_storage=true``` parameter is specified, then Openshift metrics will create PVC and use it
as storage space for cassandra pod withing Openshift metrics.
Please note that all what applies for cassandra database performances [cassandra link](http://www.planetcassandra.org/blog/impact-of-shared-storage-on-cassandra/ ) for case it
it is installed out of Openshift metrics, also applies on cassandra when deployed as part of Openshift Metrics

- If `persistent_storage=false` is used with intention for metrics data not to live longer than pod lifetime,
then it is recommended to design openshift installation to have `/var` on separate partition ( to accommodate `/lib/origin/openshift.local.volumes/pods`)
This is necessary as space under `/var/lib/origin/openshift.local.volumes/pods` will be used for pods by default as location where to store pod data on Openshift nodes,
and it is necessary to ensure that massive metrics data collection will not lead to filling up storage space on openshift node.
This issue should be solved when issue [Initial support for pod eviction based on disk](https://github.com/kubernetes/kubernetes/pull/27199) is closed

At this point, we assume that metrics pods are up and running after starting metrics as showed in below example

 ```
 # oc get pods -n openshift-infra
 NAME                                          READY             STATUS      RESTARTS   AGE
 hawkular-cassandra-1-l5y4g           1/1               Running     0                 17h
 hawkular-metrics-1t9so                  1/1               Running     0                 17h
 heapster-febru                               1/1               Running     0                  17h

 ```
if this is not the case, please check Openshift metrics documentation and ensure Openshift metrics pods are up and running.

### Openshift Metrics dimensioning best practices

Openshift metrics uses Cassandra database as datastore for metrics and current version of Cassandra builtin in
 Openshift metrics is `CASANDRA_VERSION=2.2.4` with `MAX_HEAP_SIZE=512M` and `NEW_HEAP_SIZE=100M`. It is assumed that these values should
 cover most of Openshift metrics installations. It is possible to change these values in [cassandra docker file](https://github.com/openshift/origin-metrics/blob/master/cassandra/Dockerfile)
 prior starting metrics.


Default time for Openshift metrics data preservation is specified with parameter `METRIC_DURATION`  in  [`metrics.yaml`](https://github.com/openshift/origin-metrics/blob/master/metrics.yaml) is 7 (days).
This means Openshift metrics will keep data for 7 days before it start to purge old ones from cassandra database and to free
up storage space.

In tests where 1000 pods were monitored by Openshift metrics and latest Openshift metrics images, it was noticed that for 1000 pods during 24h metrics data
collection will cause that cassandra storage space grow at around 2.5 GB.

Based on tests we can say that Openshift Metrics will collect apprimately `0.1MB` of data per hour for Openshift pod

```
2.5*10^9)/1000)/24)/10^6 = 0.1 MB/hour
```
Graphically that is presented on graph below

< insert graph here - ekuric  >


If default value of 7 (days) for `METRIC_DURATION` is preserved, then it is expected to  that cassandra pod storage requirement
would 17.5 GB / week for test case of 1000 pods in Openshift cluster installation.

This value will grow up if more pods is observed and/or if `METRIC_DURATION` parameter is increased.



### Scaling Openshift Metrics pods

One set of metrics pods ( one cassandra/hawkular/heapster pod ) monitored without any issues up to 10k pods
and there was not necessary to increase number of Openshift metrics pods.

It is recommended to pay attention on load imposed on nodes where Openshift metrics pods runs and based on that decide
if necessary to scale out number of Openshift metrics pods.

To scale out cassandra pods to count two replicas , run below
```
# oc scale -n openshift-infra --replicas=2 rc hawkular-cassandra-1
```

If Openshhift metrics is deployed with `persistant_storage=true`, it is necessary before scaling out number of Openshift metrics
cassandra pods to create PV ( Persistent Volume )  which will be used by new cassandra pods. This needs to be done in advance


To scale out number of Openshift metrics hawkualar pods to two replicas, run below

```
oc scale -n openshift-infra --replicas=2 rc hawkular-metrics
```
### HPA - Horizontal Pod Autoscaling - TBD will this be an option
