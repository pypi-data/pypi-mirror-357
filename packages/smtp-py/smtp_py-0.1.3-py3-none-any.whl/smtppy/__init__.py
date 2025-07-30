_API_KEY = None

def setapikey(key):
    
    global _API_KEY
    _API_KEY = key

def getapikey():
    
    import os
    return _API_KEY or os.getenv("xapikey")


from .smtppy import (
    listdomains,
    createdomain,
    getdomain,
    deletedomain,
    updatedomain,
    listaccounts,
    createaccount,
    getaccount,
    deleteaccount,
    updateaccount,
    listmailboxes,
    createmailbox,
    getmailbox,
    deletemailbox,
    updatemailbox,
    listmessages,
    getmessage,
    deletemessage,
    updatemessage,
    getmessagesource,
    downloadmessage,
    movemessage,
    listtoken,
    createtoken,
    gettoken,
    deletetoken
)
