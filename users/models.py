import json
from main import config

# users = [
#     {"id": "default", "channels": config.channels},
# ]
# # create json
# with open("users_settings.json", "w") as f:
#     json.dump(users, f, indent=4)

# так не пойдёт, нельзя читать настройки только при запуске бота!!!!!!!!!!!!!!!!!
users_settings: list[dict] = json.load(open("users/users_settings.json"))
