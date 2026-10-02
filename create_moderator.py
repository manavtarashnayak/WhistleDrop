from app.database import SessionLocal
from app.models import Moderator
from app.auth import hash_password

db = SessionLocal()

moderator = Moderator(
    username="admin",
    password_hash=hash_password("min@123")
)

db.add(moderator)
db.commit()

print("Moderator created successfully!")

db.close()