import requests
from dotenv import load_dotenv
import os
import sys
load_dotenv()
xapikey = os.getenv('xapikey')
headers = {
    'X-API-KEY': xapikey,
    'Accept': 'application/json',
}
if not xapikey:
    print('''Please provide "xapikey". If you don't have an API key yet, create a new one on the API Keys page (https://smtp.dev/tokens/).''')
    sys.exit()
def listdomains(isActive=True, page=1):
    params = {
    'isActive': isActive,
    'page': page,
    }

    response = requests.get('https://api.smtp.dev/domains', params=params, headers=headers)
    return(response.json())
def createdomain(domain, isActive=True):
    if not domain:
        print('''Please provide "domain"''')
    json_data = {
    'domain': domain,
    'isActive': isActive,
    }

    response = requests.post('https://api.smtp.dev/domains', headers=headers, json=json_data)
    return(response.json())
def getdomain(id):
    response = requests.get(f'https://api.smtp.dev/domains/{id}', headers=headers)
    return(response.json())
def deletedomain(id):
    response = requests.delete(f'https://api.smtp.dev/domains/{id}', headers=headers)
    return(response.json())
def updatedomain(id, isActive=True):
    data = {"isActive": isActive}
    response = requests.patch(f'https://api.smtp.dev/domains/{id}', headers=headers, data=data)
    return(response.json())
def listaccounts(address, isActive=True, page=1):
    response = requests.get(f'https://api.smtp.dev/accounts?address={address}&isActive={isActive}&page={page}', headers=headers)
    return(response.json())
def createaccount(address, password):
    json_data = {
    'address': address,
    'password': password,
    }

    response = requests.post('https://api.smtp.dev/accounts', headers=headers, json=json_data)
    return(response.json())
def getaccount(accountId):
    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}', headers=headers)
    return(response.json())
def deleteaccount(accountId):
    response = requests.delete(f'https://api.smtp.dev/accounts/{accountId}', headers=headers)
    return(response.json())
def updateaccount(password, accountId, isActive=True):
    json_data = {
    "password": password,
    "isActive": isActive
    }
    response = requests.patch(f'https://api.smtp.dev/accounts/{accountId}', headers=headers, data=json_data)
    return(response.json())
def listmailboxes(accountId, page=1):
    params = {
    'page': page,
    }

    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}/mailboxes', params=params, headers=headers)
    return(response.json())
def createmailbox(path, accountId):
    json_data = {
    'path': path,
    }

    response = requests.post(f'https://api.smtp.dev/accounts/{accountId}/mailboxes', headers=headers, json=json_data)
    return(response.json())
def getmailbox(accountId, mailboxId):
    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}', headers=headers)
    return(response.json())

def deletemailbox(accountId, mailboxId):
    response = requests.delete(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}', headers=headers)
    return(response.json())

def updatemailbox(path, accountId, id):
    json_data = {
    "path": path
    }
    response = requests.patch(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{id}', headers=headers, data=json_data)
    return(response.json())

def listmessages(accountId, mailboxId, page=1):
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
    response = requests.get(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}', headers=headers)
    return(response.json())
def deletemessage(accountId, mailboxId, id):
    response = requests.delete(f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}', headers=headers)
    return(response.json())
def updatemessage(accountId, mailboxId, id, expiresAt, isRead=True, isFlagged=True, autoDeleteEnabled=True):
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
    response = requests.get(
    f'https://api.smtp.dev/accounts/{accountId}/mailboxes/{mailboxId}/messages/{id}/source',
    headers=headers,
    )
    return(response.json())
def downloadmessage(accountId, mailboxId, id, attachmentId, o, metadata=False):
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
    params = {
    'page': page,
    }

    response = requests.get('https://api.smtp.dev/tokens', params=params, headers=headers)
    return(response.json())

def createtoken(name='Default', description='Default'):
    json_data = {
    'name': name,
    'description': description,
    }
    

    response = requests.post('https://api.smtp.dev/tokens', headers=headers, json=json_data)
    return(response.json())
def gettoken(id):
    response = requests.get(f'https://api.smtp.dev/tokens/{id}', headers=headers)
    return(response.json())

def deletetoken(id):
    response = requests.delete(f'https://api.smtp.dev/tokens/{id}', headers=headers)
    return(response.json())
