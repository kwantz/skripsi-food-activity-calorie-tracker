import jwt
from datetime import datetime, timedelta
from django.core.exceptions import ObjectDoesNotExist
from fact.models import User

class JWT:
    def __init__(self):
        self.key = 'V1nS0n-S1lF1_3R1cK'

    def encode(self, data):
        data["exp"] = datetime.utcnow() + timedelta(days=1)
        return jwt.encode(data, self.key, algorithm="HS256").decode("utf-8")

    def decode(self, token):
        try:
            data = jwt.decode(token, self.key, algorithms="HS256")
            id  = data.get("id", 0)
            name = data.get("name", "")
            email = data.get("email", "")
            return User.objects.get(id=id, name=name, email=email)

        except jwt.ExpiredSignatureError:
            return None

        except ObjectDoesNotExist:
            return None