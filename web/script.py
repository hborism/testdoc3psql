from app import *

henrik = Player('henrik', 'henrik@example.com')
axel = Player('axel', 'axel@example.com')

db.session.add(henrik)
db.session.add(axel)
db.session.commit()