from main import db, User

db.create_all()

# insert users's usernames and passwords
user_one = User(username="bigbuck", password="bunny")
user_two = User(username="ffmpeg", password="rocks")
user_three = User(username="mad", password="max")

db.session.add(user_one)
db.session.add(user_two)
db.session.add(user_three)
db.session.commit()
