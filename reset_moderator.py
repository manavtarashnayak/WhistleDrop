from app.database import SessionLocal
from app.models import Moderator
from app.auth import hash_password

db = SessionLocal()

moderator = db.query(Moderator).filter(
    Moderator.username == "admin"
).first()

if moderator:
    moderator.password_hash = hash_password("Whistle@123")
else:
    moderator = Moderator(
        username="admin",
        password_hash=hash_password("Whistle@123")
    )
    db.add(moderator)

db.commit()

print("Moderator password reset successfully!")

db.close()