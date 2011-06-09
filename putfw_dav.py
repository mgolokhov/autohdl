import httplib, urllib
import urllib2
#import lxml
#from lxml.etree import Element, ElementTree, HTML
import os
import sys
import base64

import autohdl.lib.yaml as yaml



def make_req(method,uri,params,header):
    conn = httplib.HTTPConnection("cs.scircus.ru")
    conn.request(method, uri, params, header)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    print response.status, response.reason
    if response.status > 205:
        print data
    return response


def put_firmware(fw_file):
        fi=open(fw_file,"rb")
        data = fi.read();
        fi.close();
        data_len = len(data)
        
        username, password = authenticate()

        fw_name = os.path.basename(fw_file)

        base64string = base64.encodestring(
                '%s:%s' % (username, password))[:-1]
        authheader =  "Basic %s" % base64string
        
        headers_head = {
            "Content-Type" :  "application/binary",
            "Authorization": authheader
        }

        headers_move = {
            "Content-Type" :  "application/binary",
            "Authorization": authheader,
            "Destination" : "http://cs.scircus.ru/test/distout/rtl/"+fw_name,
            "Depth" : "infinity"
        }


        headers = {
            "Content-Type" :  "application/binary",
            "Authorization": authheader,
            "Content-Length" : data_len
           }
        

        n_tryes = 5

        while n_tryes >0:
            print "Checks if file exists on the server"
            resp = make_req("HEAD","/test/distout/rtl/" + fw_name,"",headers_head)
            if resp.status == 200:
                print "File exists. Remove it"
                resp = make_req("DELETE", "/test/distout/rtl/" + fw_name, "", headers_head)
                
            print "Downloading it to server with name tmpfile (%d) ..." % n_tryes
            resp = make_req("PUT", "/test/distout/rtl/tmpfile" , data, headers)
            if resp.status >= 400:
                n_tryes = n_tryes - 1
            else:
                n_tryes = 0   
        if resp.status < 400:
            print "Rename to " + fw_name
            resp = make_req("MOVE", "/test/distout/rtl/tmpfile", "", headers_move)
   
    
def authenticate():
  ask = False
  
  path = sys.prefix + '/Lib/site-packages/autohdl_cfg/open_sesame'
  if os.path.exists(path):
    content = yaml.load(open(path, 'r'))
    try:
      username = base64.decodestring(content[base64.encodestring('username')])
      password = base64.decodestring(content[base64.encodestring('password')])
    except KeyError as e:
      ask = True
  else:  
    ask = True

  while ask:
    username = raw_input('user:')
    password = raw_input('password:')
    request = urllib2.Request("http://cs.scircus.ru/test/distout/rtl")
    base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    try:
      result = urllib2.urlopen(request)
      contentYaml = {
                     base64.encodestring('username'): base64.encodestring(username),
                     base64.encodestring('password'): base64.encodestring(password)} 
      yaml.dump(contentYaml, open(path, 'wb'), default_flow_style = False)
      break
    except urllib2.HTTPError as e:
      quit = raw_input('Wrong user/password, try again hit Enter; To quit hit Q.')
      if quit.lower() == 'q':
        print 'Exit...'
        sys.exit(0)
  
  return username, password


if __name__ == "__main__":
	put_firmware("putfw_dav.py")

    

