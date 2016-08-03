import datetime
from datetime import datetime
from app import db
from flask import jsonify
import json

'''
---------------------------------------------------------------------
 ____        _        _                    __  __           _      _
|  _ \  __ _| |_ __ _| |__   __ _ ___  ___|  \/  | ___   __| | ___| |
| | | |/ _` | __/ _` | '_ \ / _` / __|/ _ \ |\/| |/ _ \ / _` |/ _ \ |
| |_| | (_| | || (_| | |_) | (_| \__ \  __/ |  | | (_) | (_| |  __/ |
|____/ \__,_|\__\__,_|_.__/ \__,_|___/\___|_|  |_|\___/ \__,_|\___|_|
---------------------------------------------------------------------
'''


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return {"id":self.id, "name":self.name}

    def serialize(self):
        return {"id":self.id, "name":self.name}



class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(40))
    email = db.Column(db.String(120), unique=True)
    hcp = db.Column(db.Integer)
    profile_picture_id = db.Column(db.String(36), unique=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    access_token = db.Column(db.String(42))
    password = db.Column(db.String(50))
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, first_name, last_name, email, hcp, profile_picture_id, club_id, access_token, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hcp = hcp
        self.profile_picture_id = profile_picture_id
        self.club_id = club_id
        self.access_token = access_token
        self.password = password

    def __repr__(self):
        return '<Player %r>' % self.email



class Friends(db.Model):
    id1 = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    id2 = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)

    def __init__(self, id1, id2):
        self.id1=id1
        self.id2=id2



class Course(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(40))
	number_of_holes = db.Column(db.Integer)
	club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

	def __init__(self, name, number_of_holes, club_id):
		self.name = name
		self.number_of_holes = number_of_holes
		self.club_id = club_id

	def __repr__(self):
		return '<Course %r>' % self.name



class Hole(db.Model):
    tee_no = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    par = db.Column(db.Integer)
    index = db.Column(db.Integer)
    red_tee = db.Column(db.Integer)
    blue_tee = db.Column(db.Integer)
    yellow_tee = db.Column(db.Integer)
    white_tee = db.Column(db.Integer)

    def __init__(self, tee_no, course_id, par, index, red_tee, blue_tee, yellow_tee, white_tee):
        self.tee_no = tee_no
        self.course_id = course_id
        self.par = par
        self.index = index
        self.red_tee = red_tee
        self.blue_tee = blue_tee
        self.yellow_tee = yellow_tee
        self.white_tee = white_tee

    def __repr__(self):
        return '<Hole %r>' % self.tee_no



class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    created_by_player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, course_id, created_by_player_id):
        self.course_id = course_id
        self.created_by_player_id = created_by_player_id

    def __repr__(self):
        return '<Round %r>' % self.id



class Score(db.Model):
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)

    def __init__(self, round_id, player_id):
        self.round_id = round_id
        self.player_id = player_id



'''CAREFUL HERE: since hole_no is not a foreign key to hole.hole_no and hole.course_id
it might be possible to add scores to holes that do not exist if not careful'''
class ScoreHole(db.Model):
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    hole_no = db.Column(db.Integer, primary_key=True)
    shots = db.Column(db.Integer, nullable=False)

    def __init__(self, round_id, player_id, hole_no, shots):
        self.round_id = round_id
        self.player_id = player_id
        self.hole_no = hole_no
        self.shots = shots
