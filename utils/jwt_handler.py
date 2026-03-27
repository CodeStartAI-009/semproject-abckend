import jwt
import datetime

# 🔥 Use strong secret (min 32 chars)
SECRET = "my_super_secure_secret_key_123456789"

def generate_token(user_id):
    payload = {
        "user_id": str(user_id),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as e:
        print("JWT ERROR:", e)
        return None