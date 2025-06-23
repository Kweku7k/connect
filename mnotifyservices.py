from pprint import pprint
import requests

API_KEY="whmBov51IDjkTtj6AAWmakuid9NljoRPFdr4Jx6rbqM4T"

# def addContactToGroup(data,groupId):
#     endPoint = 'https://api.mnotify.com/api/group'
#     apiKey = API_KEY
#     groupId = 1
#     data = {
#         'phone': '0244698970',
#         'title': 'Dr',
#         'firstname': 'Stephen',
#         'lastname': 'Strange',
#         'email': 'strange.smart@gmail.com',
#         'dob': '1979-01-01',
#         }
#     url = endPoint + '/' + groupId + '?key=' + apiKey
#     response = requests.post(url, data)
#     data = response.json()
    
# def createMnotifyGroup(group_name):
#     endPoint = 'https://api.mnotify.com/api/sms/quick'
#     api_key = API_KEY #Remember to put your own API Key here
#     data = {
#         'group_name': group_name,
#         }
#     url = endPoint + '?key=' + api_key
#     response = requests.post(url, data)
#     data = response.json()
#     pprint(data)
#     return data


def createMnotifyGroup(group_name):
    endPoint = 'https://api.mnotify.com/api/group'
    api_key = API_KEY #Remember to put your own API Key here
    data = {
        'group_name': group_name,
        'name': group_name,
        }
    url = endPoint + '?key=' + api_key
    response = requests.post(url, data)
    data = response.json()
    print("endPoint")
    print(endPoint)
    pprint(data)
    return data

def addContactToGroup(groupId, data):
    endPoint = f'https://api.mnotify.com/api/contact'
    apiKey = API_KEY
    url = endPoint + '/' + str(groupId) + '?key=' + apiKey
    response = requests.post(url, data)
    data = response.json()
    return data
    
def addMessageTemplate(template_name, message):
    endPoint = 'https://api.mnotify.com/api/template'
    apiKey = API_KEY #Remember to put your own API Key here
    data = {
        'title': template_name,
        'body': message,
        'content': message,
        }
    url = endPoint + '?key=' + apiKey
    response = requests.post(url, data)
    data = response.json()
    pprint(data)
    return data
    
def sendBulkMessage(sender, message, groupId,  templateId):
    endPoint = 'https://api.mnotify.com/api/sms/group'
    api_key = API_KEY #Remember to put your own API Key here
    data = {
        'group_id': groupId,
        'message': message,
        'sender': sender,
        'message_id':templateId
        }
    pprint(data)
    url = endPoint + '?key=' + api_key
    response = requests.post(url, json=data)
    response_data = response.json()
    pprint(response_data)    
    return response_data


def getSmsBalance():
    endpoint = "https://api.mnotify.com/api/balance/sms"
    apiKey = API_KEY
    url = endpoint + '?key=' + apiKey
    response = requests.get(url)
    data = response.json()
    pprint(data)
    return data
    
