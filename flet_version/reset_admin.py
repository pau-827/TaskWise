from passlib.hash import bcrypt
import db

db.init_db()

email = "admin@taskwise.com"
new_password = "Admin123"  # You choose new password here

new_hash = bcrypt.hash(new_password)

db.update_user_password(email, new_hash)

print("Admin password reset!")
print("NEW HASH:", new_hash)