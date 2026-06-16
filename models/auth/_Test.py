from passlib.context import CryptContext
from models.auth.user import User


from db import SessionLocal



pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)



db = SessionLocal()

user = User(
    username="admin",
    password=pwd_context.hash("123456")
)

print(user.username)
print(len(user.password))



db.add(user)
db.commit()

print("User created")

