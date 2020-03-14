from api import Api

account = {
    'vk_login': '',
    'vk_pass': '',
}

api = Api(account["vk_login"], account["vk_pass"])

account_info = api.method('users.get', fields='photo_max')[0]

print(account_info)
