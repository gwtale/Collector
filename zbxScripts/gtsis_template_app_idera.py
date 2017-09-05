#!/usr/bin/python
# server, user, pass, method, optional args

import suds.client
import sys, getopt

#ssl._create_default_https_context = ssl._create_unverified_context
soap_port = "9080"

def getPolicies():
    c = suds.client.Client('http://' + soap_host + ':' + soap_port + '/Policy2?wsdl', username=soap_user, password=soap_pass)
    first=1

    print("{")
    print('    "data":[')
    for p in c.service.getPolicies():
        if first == 0:
           print(',')
        sys.stdout.write('        {"{#POLICY_ID}":"' + p.id + '","{#POLICY_NAME}":"' + p.name + '"}')
        first=0
    print(' ')
    print('    ]')
    print("}")
    #result = c.service.getPolicies()
    #print result

def getPolicy():
    c = suds.client.Client('http://' + soap_host + ':' + soap_port + '/Policy2?wsdl', username=soap_user, password=soap_pass)
    policyData = c.service.getPolicyById(extraparameters)
    print(policyData)

def getPoliciesState():
    c = suds.client.Client('http://' + soap_host + ':' + soap_port + '/Policy2?wsdl', username=soap_user, password=soap_pass)
    for p in c.service.getPolicies():
        print("Name: " + p.name + ", State: " + p.state)

def getPolicyState():
    c = suds.client.Client('http://' + soap_host + ':' + soap_port + '/Policy2?wsdl', username=soap_user, password=soap_pass)
    policyData = c.service.getPolicyById(extraparameters)
    print(policyData.state)

def getAgents():
    c = suds.client.Client('http://' + soap_host + ':' + soap_port + '/Agent?wsdl', username=soap_user, password=soap_pass)
    for a in c.service.getAgents():
        print a

try:
    args = sys.argv[1:]
    argCount = len(args)
    if argCount == 1:
        args = ' '.join(args)
        args = args.split()
    opts, args = getopt.getopt(args,"s:u:p:m:e:h",["server=","user=","password=","method=","extraparameters=","help"])
except getopt.GetoptError:
    print 'gtsis_template_app_idera.py -s <server> -u <soap user> -p <soap password> -m <method> -e <extra parameters>'
    print 'Note: If you need to pass more than 1 extra parameter, add them between quotes and separated by commas. E.g.: -e "Arg1,Arg2,Arg3"'
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        print 'gtsis_template_app_idera.py -s <server> -u <soap user> -p <soap password> -m <method> -e <extra parameters>'
        print 'Note: If you need to pass more than 1 extra parameter, add them between quotes and separated by commas. E.g.: -e "Arg1,Arg2,Arg3"'
        sys.exit()
    elif opt in ("-s", "--server"):
        soap_host = arg
    elif opt in ("-u", "--user"):
        soap_user = arg
    elif opt in ("-p", "--password"):
        soap_pass = arg
    elif opt in ("-m", "--method"):
        method = arg
    elif opt in ("-e", "--extraparameters"):
        extraparameters = arg

methods = {"getPolicies": getPolicies,
           "getPolicy": getPolicy,
           "getPoliciesState": getPoliciesState,
           "getPolicyState": getPolicyState,
           "getAgents": getAgents
}

# RUN THE CODE
methods[method]()

