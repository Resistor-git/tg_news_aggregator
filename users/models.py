import json
from main import config

# users = [
#     {"id": "default", "channels": config.channels},
#     {"id": 5897335213, "channels": ["fontankaspb", "bbcrussian"]},
#     {"id": 111, "channels": ["foo", "bar"]},
# ]
# # create json
# with open("users_settings.json", "w") as f:
#     json.dump(users, f, indent=4)


users_settings: list[dict] = json.load(open("users/users_settings.json"))

# opens users_settings.json, if user with "id": 222 does not exist, creates it
# with open("users_settings.json", "r+") as f:
#     user_exists = False
#     for user in users:
#         if user["id"] == 222:
#             user_exists = True
#             break
#     if not user_exists:
#         users.append({"id": 222, "channels": ["foo2", "bar2"]})
#         json.dump(users, f, indent=4)

# with open("users_settings.json", "w") as f:
#     users.append({"id": 222, "channels": ["foo2", "bar2"]})
#     json.dump(users, f, indent=4)


# from dataclasses import dataclass


# @dataclass
# class User:
#     user_id: int
#     channels: list[str, ...]  # заменить на int
#
# кнопка создаёт экземпляр класса: 555555 = User(555555, ['foo', 'bar']
# pickle сохраняет его в файл пользователей?
