from git import Repo
import json, os
import urllib2
from tinydb import TinyDB, Query


def git_pull(docroot,branch, config=None):

    # hipchat = http.client.HTTPConnection('https')
    # url = "https://ivorycoconut.hipchat.com/v2/room/2990311/notification?auth_token=HegKkgyhud1zOreYxuTySQEHMlevhPIQR7WFdncb"
    directory = os.path.dirname(os.path.abspath(config['db_dir']))

    if not os.path.exists(directory):
        os.makedirs(directory)

    db = TinyDB(config['db_dir'])
    Log = Query()

    try:
        
        repo = Repo(docroot)
        origin = repo.remotes.origin
        origin.fetch()

        repo.git.checkout(branch)
        repo.git.reset('--hard',"origin/{}".format(branch))
    except Exception, e:

        if(config is not None and config['use_hipchat']):
            data = json.dumps({"color":"red","message":"Pulling FAIL","notify":False,"message_format":"text"})
            dlen = len(data)
            req = urllib2.Request(url,data,{'Content-type':'application/json', 'Content-length' : dlen})
            f = urllib2.urlopen(req)

        db.insert({"status":"failed","message":"pulling FAIL on branch : {} and docroot : {}".format(branch, docroot),"payload":str(e)})
        pass
        # send to hipchat (failed).
    else:

        if(config is not None and config['use_hipchat']):
            data = json.dumps({"color":"green","message":"Pulling OK ","notify":False,"message_format":"text"})
            dlen = len(data)
            req = urllib2.Request(url,data,{'Content-type':'application/json', 'Content-length' : dlen})
            f = urllib2.urlopen(req)

        db.insert({"status":"success","message":"pulling OK on branch : {} and docroot : {}".format(branch, docroot),"payload": None})

        pass
        #send to hipchat (success)


'''
hipchat notif.
https://ivorycoconut.hipchat.com/v2/room/2990311/notification?auth_token=HegKkgyhud1zOreYxuTySQEHMlevhPIQR7WFdncb
curl -d '{"color":"green","message":"My first notification (yey)","notify":false,"message_format":"text"}' -H 'Content-Type: application/json' https://ivorycoconut.hipchat.com/v2/room/2990311/notification?auth_token=HegKkgyhud1zOreYxuTySQEHMlevhPIQR7WFdncb
'''