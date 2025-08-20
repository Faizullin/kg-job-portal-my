import json

"""
NOT USED FOR NOW
"""


class ActionTypes:
    ERROR = "error"
    SUCCESS = "success"
    UPDATE_DAY_STREAK = 'update_day_streak'


class Action:
    def __init__(self, type: str, data):
        self.type = type
        self.data = data

    async def to_json(self):
        return json.dumps({"type": self.type, "data": self.data})

    @staticmethod
    async def from_json(json_string: str) -> 'Action':
        obj = Action('', '')
        try:
            json_object = json.loads(json_string)
            obj.type = json_object["type"]
            obj.data = json_object["data"]
        except KeyError:
            pass
        except json.JSONDecodeError as e:
            pass
        return obj

    @staticmethod
    async def error(data: str) -> str:
        return await Action(ActionTypes.ERROR, data).to_json()

    @staticmethod
    async def success(data: str = 'success') -> str:
        return await Action(ActionTypes.SUCCESS, data).to_json()
