import random
import string
import hashlib
import base64

def generate_random_string(min_length, max_length):
    length = random.randint(min_length, max_length)
    characters = string.ascii_letters + string.digits + "-._~"
    return ''.join(random.choice(characters) for _ in range(length))

def generate_code_challenge(code_verifier):
    hashed = hashlib.sha256(code_verifier.encode()).digest()
    return base64.urlsafe_b64encode(hashed).decode().rstrip('=')