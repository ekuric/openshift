## README
```delete-aws-instnace.py``` script can be used to delete aws instances based on their name
## Usage
```
$ python delete-aws-instance.py -h
usage: delete_aws_instance_class.py [-h] [--iname INAME] --istate ISTATE
                                    --action ACTION

Script to start/stop or terminate EC2 instance based on its tag prefix

optional arguments:
  -h, --help       show this help message and exit
  --iname INAME    intances Tag - instance has to be tagged in order this
                   script to work with it - untagged instances cannot be
                   changed with script tag is important to decide which
                   instances to stop/start. Eg. if instances has in tag prefix
                   qe_mysmalltest then all instances with this tag prefix will
                   be affected
  --istate ISTATE  ec2 instance state - if running, than change can be to
                   stopped, from stopped state we can either start / terminate
                   instance
  --action ACTION  what to do - stop, stop, or terminnate instance - default
                   is stop

```

script requires ```boto3``` python module to be installed on system where script is supposed to be run
and aws creditielas to be in place and working

## stop instances

in order to tagged with tag ```mytest_instnaces``` one can do

```
$ python delete_aws_instances --iname mytest_instances --istate running --action stop
```
This will look for all instances which have  ``` mytest_instaces```  in tag prefix and stop them

## start instances

in order to start all instances with above tag prefix we can do
```
$ python delete_aws_instances.py --iname mytest_instances --istate stopped --action start
```
## terminate instances

Last and most dangerous step is to terminate instances. Eg. in order to terminate all instances
prefixed as showed in above examples one can do
```
$ python delete_aws_instances.py --iname mytest_instances --istate stopped --action terminate
```
Terminate step is destructive and after it ec2 instances will be fully deleted from ec2 account
Use terminate option carefully!
