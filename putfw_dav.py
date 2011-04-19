import httplib, urllib
#import lxml
#from lxml.etree import Element, ElementTree, HTML
import os

import base64

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
        username = 'gnomik'
        password = ',f,rbgbljhrb'

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
    
if __name__ == "__main__":
	put_firmware("putfw_dav.py")
    

