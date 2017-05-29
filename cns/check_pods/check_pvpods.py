#!/usr/bin/env python

import sys
import argparse
import requests
import csv
import json
import time

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from requests.exceptions import ConnectionError

parser = argparse.ArgumentParser(description='Check pods/pv/pvc on OCP installation')
parser.add_argument("-proto", "--protocol", type=str,
                    help='Protocol openshift (Default : https)',
                    default="https")
parser.add_argument("-api", "--base_api", type=str,
                    help='Url api and version (Default : /api/v1)',
                    default="/api/v1")
parser.add_argument("-H", "--host", type=str,
                    help='Host openshift (Default : 127.0.0.1)',
                    default="127.0.0.1")
parser.add_argument("-P", "--port", type=str,
                    help='Port openshift (Default : 8443)',
                    default=8443)
parser.add_argument("-to", "--token", type=str,
                    help='File with token openshift (like -t)')
parser.add_argument("--check_pods", action='store_true',
                    help='Get information about pods')
parser.add_argument("-ns", help="The namespace where to look for parameters")
parser.add_argument("--check_pvc", action='store_true', help='Get list of PVCs elemements in desired namespace')
parser.add_argument("--check_pv", help="List of PV volumes", action='store_true')
parser.add_argument("--check_all", help="collect data for PV/PVC and PODS information ... ", action='store_true')

args = parser.parse_args()
ns = args.ns

class Openshift(object):

    def __init__(self,
                 proto='https',
                 host='127.0.0.1',
                 port=8443,
                 token=None,
                 debug=False,
                 verbose=False,
                 namespace=ns,
                 base_api='/api/v1'):

        self.proto = proto
        self.host = host
        self.port = port
        self.debug = debug
        self.verbose = verbose
        self.namespace = namespace
        self.base_api = base_api.rstrip('/')

        if token:
            self.token = token

    def get_json(self, url):

        headers = {"Authorization": 'Bearer %s' % self.token}
        try:
            r = requests.get('https://%s:%s%s' % (self.host, self.port, url),
                             headers=headers,
                             verify=False)
            parsed_json = r.json()
        except ValueError:
            print ("Unable to authenticate against OCP master", self.host, "check is token correct")
            sys.exit()
        except ConnectionError as e:
            print ("Unable to connect to OCP master", self.host, "check connection to master")
            sys.exit()

        return parsed_json

    # get all PVC from particular namespace
    def get_pvc(self, namespace=None):

        if namespace:
            self.namespace = ns
        api_pvc = '%s/namespaces/%s/persistentvolumeclaims' % (self.base_api, self.namespace)
        parsed_json = self.get_json(api_pvc)
        pvc_claims = []

        for item in parsed_json["items"]:
            pvc_claims.append(item)
            pvc_claims = sorted(pvc_claims, key=lambda k: k['metadata']['creationTimestamp'],reverse=False)

            with open("pvc_"+str(ns)+".json", "w") as allpvc:
                json.dump(pvc_claims, allpvc, indent=4)

        # sorted - get stuff properly printed

        with open("pvc_"+str(ns)+".csv", 'wb') as cvsout:
            csv_out = csv.writer(cvsout)
            csv_out.writerow(['PVC Name', 'PVC Size' 'PVC Create Time','PVC Create Time - TZ' 'PVC Namespace'])
            for pvc in pvc_claims:
                csv_out.writerow([pvc["metadata"]["name"], pvc['spec']['resources']['requests']['storage'],
                                  int(time.mktime(time.strptime(pvc["metadata"]["creationTimestamp"], '%Y-%m-%dT%H:%M:%SZ'))),
                                  pvc["metadata"]["creationTimestamp"],
                                  pvc["metadata"]["namespace"]])

    def get_pv(self,namespace=None):

        if namespace:
            self.namespace = ns

        api_pv = '%s/persistentvolumes' % (self.base_api)

        parsed_json = self.get_json(api_pv)
        pv_volumes = []

        for item in parsed_json["items"]:
            pv_volumes.append(item)
            pv_volumes = sorted(pv_volumes, key=lambda k: k['metadata']['creationTimestamp'], reverse=False)
            with open("pv_"+str(ns)+".json", "w") as allpv:
                json.dump(pv_volumes, allpv, indent=4)


        with open("pv_"+str(ns)+".csv", 'wb') as csv_pv:
            csv_out = csv.writer(csv_pv)
            csv_out.writerow(['PV Name', 'PVC Name', 'PV Size', 'PV Create Time', 'PV Create Time - TZ', 'PV Namespace'])
            for pv in pv_volumes:
                if pv["spec"]["claimRef"]["namespace"] == ns:
                    csv_out.writerow([pv["metadata"]["name"],pv["spec"]["claimRef"]["name"],pv["spec"]["capacity"]["storage"],
                                      int(time.mktime(time.strptime(pv["metadata"]["creationTimestamp"],'%Y-%m-%dT%H:%M:%SZ'))),
                                      pv["metadata"]["creationTimestamp"],
                                      pv["spec"]["claimRef"]["namespace"]])

    def get_pods(self, namespace=None):

        if namespace:
            self.namespace = ns

        api_pods = '%s/namespaces/%s/pods' % (self.base_api, self.namespace)
        parsed_json = self.get_json(api_pods)
        pods = []

        # sort pods based on creationTime
        for item in parsed_json["items"]:
            pods.append(item)
            pods = sorted(pods, key=lambda k: k["status"]["containerStatuses"][0]["state"]["running"]["startedAt"],reverse=False)
            with open("pods_"+str(ns)+".json", "w") as allpods:
                json.dump(pods,allpods, indent=4)

        with open("pods_"+str(ns)+".csv", 'wb') as csv_pods:
            csv_out = csv.writer(csv_pods,delimiter=",")
            csv_out.writerow(['Pod Name', "Pod Create Time", "Pod Create Time - TZ",
                              "Pod StartTime", "Pod StartTime - TZ", "Pod StartedAt Time",
                              "Pod StartedAt Time - TZ",
                              "Pod Namespace", "PVC Name"])
            # todo - fix issue where this part fail if *all* pods are not ready - ie. there is not valid state
            for pod in pods:
                csv_out.writerow([pod["metadata"]["name"], int(time.mktime(time.strptime(pod["metadata"]["creationTimestamp"], '%Y-%m-%dT%H:%M:%SZ'))),
                                  pod["metadata"]["creationTimestamp"],
                                  int(time.mktime(time.strptime(pod["status"]["startTime"],'%Y-%m-%dT%H:%M:%SZ'))),
                                  pod["status"]["startTime"],
                                  int(time.mktime(time.strptime(pod["status"]["containerStatuses"][0]["state"]["running"]["startedAt"],'%Y-%m-%dT%H:%M:%SZ'))),
                                  pod["status"]["containerStatuses"][0]["state"]["running"]["startedAt"],
                                  pod["metadata"]["namespace"], pod["spec"]["volumes"][0]["persistentVolumeClaim"]["claimName"]])

if __name__ == "__main__":

    # https://docs.openshift.com/enterprise/3.0/rest_api/openshift_v1.html
    if not args.token:
        parser.print_help()
        sys.exit()

    myos = Openshift(host=args.host,
                     port=args.port,
                     token=args.token,
                     proto=args.protocol,
                     base_api=args.base_api)

    if args.check_pvc:
        myos.get_pvc()

    if args.check_pods:
        myos.get_pods()

    if args.check_pv:
        myos.get_pv()

    if args.check_all:
        myos.get_pv()
        myos.get_pvc()
        myos.get_pods()


