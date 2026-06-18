import secrets
import string

def genth():
    chars = string.ascii_uppercase + string.digits

    random_part = "".join(
        secrets.choice(chars)
        for _ in range(11)
    )

    return f"NTH-001-{random_part}"