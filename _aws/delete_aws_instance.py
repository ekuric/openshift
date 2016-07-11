#!/usr/bin/env python

# script to start, stop, or delete/terminate EC2 instance on EC2 cloud based on instance name
# License : GPL2
__author__ = "elko"

import boto3
import argparse
import botocore

class DeleteInstance():

    def __init__(self,iname):

        """
        This script expect that amazon credentials are configured on machine where executed
        check http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
        """
        ec2 = boto3.resource("ec2")
        global reservations
        reservations = ec2.instances.filter(Filters=[{'Name':'instance-state-name','Values':[istate]}])

    def stop_instance(self, iname):
        self.iname = iname

        try:
            for instance in reservations:
                try:
                    if str(instance.tags[0].values()[0]).startswith(iname):
                        print ("Stopping instance with instance id", instance.id, "and instance tag: ", instance.tags)
                        instance.stop()
                except TypeError:
                    print ("Exception happened - seems some instances are not taggeed --  we will proceed")
        except botocore.exceptions.ClientError as err:
            print ("exception happended:", err.response['Error']['Code'])
        else:
            print ("ec2 instance with instance-id stopped")


    def start_instance(self,iname):
        self.iname = iname
        try:
            for instance in reservations:
                try:
                    if str(instance.tags[0].values()[0]).startswith(iname):
                        print ("Starting instances with tag / name ", instance.tags)
                        print (instance.id)
                        sys.exit(0)
                        instance.start()
                except TypeError:
                    print ("Exception happened - seems some instances are not taggeed --  we will proceed")
        except botocore.exceptions.ClientError as err:
            print ("excpetion happened:", err.response['Error']['Code'])
        else:
            print ("ec2 instance with tag started")


    def terminate_instance(self,iname):
        self.iname = iname
        # figure out is better approach to terminate instance directly and avoiding stop step, this works too - could be a bit dangerous
        # leaving it as is - first stop instances and then if all is fine terminate them in next run
        try:
            for instance in reservations:
                try:
                    if str(instance.tags[0].values()[0]).startswith(iname):
                        instance.terminate()
                        print ("Terminating instance with instance id", instance.id, "and instance tag", instance.tags)
                except TypeError:
                    print ("Exception happened - seems some instances are not taggeed --  we will proceed")

        except botocore.exceptions.ClientError as err:
            print ("exception happened", err.response['Error']['Code'])
        else:
            print ("ec2 instances terminated")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Script to start/stop or terminate EC2 instance based on its tag prefix")
    parser.add_argument("--iname", help=" intances Tag - instance has to be tagged in order this script to work with it - untagged instances cannot be changed with script"
                                        " tag is important to decide which instances to stop/start. Eg. if instances has in tag prefix qe_mysmalltest then all"
                                        " instances with this tag prefix will be affected", type=str)
    parser.add_argument("--istate", help="ec2 instance state - if running, than change can be to stopped, from stopped state we can either start / terminate instance ",required=True, type=str)
    parser.add_argument("--action", help="what to do - stop, stop, or terminnate instance - default is stop", default="stop", required=True, type=str)
    args = parser.parse_args()
    iname = args.iname
    istate = args.istate
    action = args.action
    delete_instance = DeleteInstance(iname)

    if action == "stop":
        delete_instance.stop_instance(iname)
    elif action == "terminate":
        delete_instance.terminate_instance(iname)
    elif action == "start":
        delete_instance.start_instance(iname)
