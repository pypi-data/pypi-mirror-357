import requests
from dotenv import load_dotenv
import os
import sys
from . import getapikey
load_dotenv()

def getheaders():
    xapikey = getapikey()
    if not xapikey:
        print('''Please provide "xapikey". If you don't have an API key yet, create a new one on the API Keys page (https://smtp.dev/tokens/).''')
        sys.exit()
    return {
        'X-API-KEY': xapikey,
        'Accept': 'application/json',
    }


def listdomains(isActive=True, page=1):
    headers = getheaders()
    params = {
    'isActive': isActive,
    'page': page,
    }

    response = requests.get('https://api.smtp.dev/domains', params=params, headers=headers)
    return(response.json())
def createdomain(domain, isActive=True):
    headers = getheaders()
    if not domain:
        print('''Please provide "domain"''')
    json_data = {
    'domain': domain,
    'isActive': isActive,
    }

    response = requests.post('https://api.smtp.dev/domains', headers=headers, json=json_data)
    return(response.json())
def getdomain(id):
    headers = getheaders()
    response = requests.get(f'https://api.smtp.dev/domains/{id}', headers=headers)
    return(response.json())
def deletedomain(id):
    headers = getheaders()
    response = requests.delete(f'https://api.smtp.dev/domains/{id}', headers=headers)
    return(response.json())
def updatedomain(id, isActive=True):
    headers = getheaders()
    data = {"isActive": isActive}
    response = requests.patch(f'https://api.smtp.dev/domains/{id}', headers=headers, data=data)
    return(response.json())
def listaccounts(address, isActive=True, page=1):
    headers = getheaders()
    response = requests.get(f'https://api.smtp.dev/accounts?address={address}&isActive={isActive}&page={page}', headers=headers)
    return(response.json())
def createaccount(address, password):
    headers = getheaders()
    json_data = {
    'address': address,
    'password': password,
    }

    response = requests.post('https://api.smtp.dev/accounts', headers=headers, json=json_data)
    return(response.json())
def getaccount(accountId):
    headers = getheaders()
    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}', headers=headers)
    return(response.json())
def deleteaccount(accountId):
    headers = getheaders()
    response = requests.delete(f'https://api.smtp.dev/accounts/{accountId}', headers=headers)
    return(response.json())
def updateaccount(password, accountId, isActive=True):
    headers = getheaders()
    json_data = {
    "password": password,
    "isActive": isActive
    }
    response = requests.patch(f'https://api.smtp.dev/accounts/{accountId}', headers=headers, data=json_data)
    return(response.json())
def listmailboxes(accountId, page=1):
    headers = getheaders()
    params = {
    'page': page,
    }

    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}/mailboxes', params=params, headers=headers)
    return(response.json())
def createmailbox(path, accountId):
    headers = getheaders()
    json_data = {
    'path': path,
    }

    response = requests.post(f'https://api.smtp.dev/accounts/{accountId}/mailboxes', headers=headers, json=json_data)
    return(response.json())
def getmailbox(accountId, mailboxId):
    headers = getheaders()
    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}', headers=headers)
    return(response.json())

def deletemailbox(accountId, mailboxId):
    headers = getheaders()
    response = requests.delete(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}', headers=headers)
    return(response.json())

def updatemailbox(path, accountId, id):
    headers = getheaders()
    json_data = {
    "path": path
    }
    response = requests.patch(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{id}', headers=headers, data=json_data)
    return(response.json())

def listmessages(accountId, mailboxId, page=1):
    headers = getheaders()
    params = {
    'page': page,
    }

    response = requests.get(
    f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages',
    params=params,
    headers=headers,
    )
    return(response.json())
def getmessage(accountId, mailboxId, id):
    headers = getheaders()
    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}', headers=headers)
    return(response.json())
def deletemessage(accountId, mailboxId, id):
    headers = getheaders()
    response = requests.delete(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}', headers=headers)
    return(response.json())
def updatemessage(accountId, mailboxId, id, expiresAt, isRead=True, isFlagged=True, autoDeleteEnabled=True):
    headers = getheaders()
    json_data = {
    "isRead": isRead,
    "isFlagged": isFlagged,
    "autoDeleteEnabled": autoDeleteEnabled,
    "expiresAt": expiresAt
    }
    response = requests.patch(
    f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}',
    headers=headers,
    data=json_data,
    )
    return(response.json())
def getmessagesource(accountId, mailboxId, id):
    headers = getheaders()
    response = requests.get(
    f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}/source',
    headers=headers,
    )
    return(response.json())
def downloadmessage(accountId, mailboxId, id, attachmentId, o, metadata=False):
    headers = getheaders()
    if metadata == False:
        response = requests.get(
        f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}/attachment/{attachmentId}',
        headers=headers,
        )
        if response.status_code == 200:
            with open(o, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            return(response.json())

    elif metadata==True:
        response = requests.get(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}', headers=headers)
        return(response.json())
    else:
        return('''Error: "metadata". Please provide e.g. metadata=True''')
def movemessage(accountId, mailboxId, id, NewmailboxId):
    headers = getheaders()
    json_data = {
    'mailbox': NewmailboxId,
    }

    response = requests.put(
    f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}/move',
    headers=headers,
    json=json_data,
    )
    return(response.json())

def listtoken(page=1):
    headers = getheaders()
    params = {
    'page': page,
    }

    response = requests.get('https://api.smtp.dev/tokens', params=params, headers=headers)
    return(response.json())

def createtoken(name='Default', description='Default'):
    headers = getheaders()
    json_data = {
    'name': name,
    'description': description,
    }
    

    response = requests.post('https://api.smtp.dev/tokens', headers=headers, json=json_data)
    return(response.json())
def gettoken(id):
    headers = getheaders()
    response = requests.get(f'https://api.smtp.dev/tokens/{id}', headers=headers)
    return(response.json())

def deletetoken(id):
    headers = getheaders()
    response = requests.delete(f'https://api.smtp.dev/tokens/{id}', headers=headers)
    return(response.json())
