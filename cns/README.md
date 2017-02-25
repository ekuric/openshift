### Usage

```
#python cns-topology.py --cnsnodesfile <nodesfile.yaml> 
```
An example of nodesfile.yaml is cnsnodes.yaml

```---
clusters:
- nodes:
  - node:
      hostnames:
        manage:
        - fqdn ( as per oc get nodes ) 
        storage:
        - 192.168.10.100
      zone: 1
    devices:
    - "/dev/sdx"
    - "/dev/sdy"
  - node:
       hostnames:
        manage:
         - fqdn ( name from oc get nodes ) 
        storage:
         - 192.168.10.102
       zone: 2
     devices:
     - "/dev/sdx"
     - "/dev/sdy"

```
add more nodes as necessesary

The `topology.json` will be generated which can be later used in 

```
#cns-deploy -y -c oc -n <namespace> -g topology.json
```
`heketi-client` provides generic `topology-sample.json` file which can be used directly. I find yaml easier to 
read and work with 
