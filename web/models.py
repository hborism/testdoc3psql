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
    name = db.Column(db.String(50) ,primary_key=True)
    info = db.Column(db.String(100))
    logo_id = db.Column(db.String(42), unique=True)
    cover_picture_id = db.Column(db.String(42), unique=True)

    def __init__(self, name, info, logo_id, cover_picture_id):
        self.name = name
        self.info = info
        self.logo_id = logo_id
        self.cover_picture_id = cover_picture_id

    def __repr__(self):
        return {"info":self.info, "name":self.name}

    def serialize(self):
        return {"info":self.info, "name":self.name, "logo_id": self.logo_id, "cover_picture_id":self.cover_picture_id}



class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(40))
    email = db.Column(db.String(50), unique=True)
    hcp = db.Column(db.Integer)
    profile_picture_id = db.Column(db.String(42), unique=True)
    cover_picture_id = db.Column(db.String(42), unique=True)
    club_name = db.Column(db.String(50), db.ForeignKey('club.name'))
    access_token = db.Column(db.String(42), unique=True)
    password = db.Column(db.String(50))
    avg_score = db.Column(db.Integer)
    par_streak = db.Column(db.Integer)
    birdie_streak = db.Column(db.Integer)
    best_club_id = db.Column(db.String(50), db.ForeignKey('club.name'))
    best_hole = db.Column(db.Integer)
    created = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, first_name, last_name, email, hcp, profile_picture_id, cover_picture_id, club_name, access_token, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hcp = hcp
        self.profile_picture_id = profile_picture_id
        self.cover_picture_id = cover_picture_id
        self.club_name = club_name
        self.access_token = access_token
        self.password = password

    def __repr__(self):
        return '<Player %r>' % self.email

    def serialize(self):
        return {"id":self.id, "first_name":self.first_name, "last_name":self.last_name, "email":self.email, "hcp":self.hcp, "club_name":self.club_name, "profile_picture_id":self.profile_picture_id, "cover_picture_id":self.cover_picture_id}



class Friend(db.Model):
    id1 = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    id2 = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, id1, id2):
        self.id1=id1
        self.id2=id2

    def serialize(self):
        return {"id1":self.id1, "id2":self.id2, "timestamp":self.timestamp}


class Friendrequest(db.Model):
    request_sender = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    request_receiver = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)

    def __init__(self, request_sender, request_receiver):
        self.request_receiver = request_receiver
        self.request_sender = request_sender

    def serialize(self):
        return {"request_sender":self.request_sender, "request_receiver":self.request_receiver}



class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    club_name = db.Column(db.String(50), db.ForeignKey('club.name'))
    par1 = db.Column(db.Integer)
    par2 = db.Column(db.Integer)
    par3 = db.Column(db.Integer)
    par4 = db.Column(db.Integer)
    par5 = db.Column(db.Integer)
    par6 = db.Column(db.Integer)
    par7 = db.Column(db.Integer)
    par8 = db.Column(db.Integer)
    par9 = db.Column(db.Integer)
    par10 = db.Column(db.Integer)
    par11 = db.Column(db.Integer)
    par12 = db.Column(db.Integer)
    par13 = db.Column(db.Integer)
    par14 = db.Column(db.Integer)
    par15 = db.Column(db.Integer)
    par16 = db.Column(db.Integer)
    par17 = db.Column(db.Integer)
    par18 = db.Column(db.Integer)

    def __init__(self, name, club_name ,par1, par2, par3, par4, par5, par6, par7, par8, par9, par10, par11, par12, par13, par14, par15, par16, par17, par18):
        self.name = name
        self.club_name = club_name
        self.par1 = par1
        self.par2 = par2
        self.par3 = par3
        self.par4 = par4
        self.par5 = par5
        self.par6 = par6
        self.par7 = par7
        self.par8 = par8
        self.par9 = par9
        self.par10 = par10
        self.par11 = par11
        self.par12 = par12
        self.par13 = par13
        self.par14 = par14
        self.par15 = par15
        self.par16 = par16
        self.par17 = par17
        self.par18 = par18

    def __repr__(self):
        return '<Course %r>' % self.name



class Hole(db.Model):
    hole_no = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
    index = db.Column(db.Integer)
    red_tee = db.Column(db.Integer)
    blue_tee = db.Column(db.Integer)
    yellow_tee = db.Column(db.Integer)
    white_tee = db.Column(db.Integer)

    def __init__(self, hole_no, course_id, index, red_tee, blue_tee, yellow_tee, white_tee):
        self.hole_no = hole_no
        self.course_id = course_id
        self.index = index
        self.red_tee = red_tee
        self.blue_tee = blue_tee
        self.yellow_tee = yellow_tee
        self.white_tee = white_tee

    def __repr__(self):
        return '<Hole %r>' % self.hole_no

    def serialize(self):
        return {"hole_no":self.hole_no, "course_id":self.course_id, "index":self.index, "red_tee":self.red_tee, "blue_tee":self.blue_tee, "yellow_tee": self.yellow_tee, "white_tee": self.white_tee}



class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    created_by_player_id= db.Column(db.Integer, db.ForeignKey('player.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, course_id, created_by_player_id, round_token):
        self.course_id = course_id
        self.created_by_player_id = created_by_player_id
        self.round_token = round_token

    def __repr__(self):
        return '<Round %r>' % self.id



class Score(db.Model):
    round_id = db.Column(db.Integer, db.ForeignKey('round.id'), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    hole1 = db.Column(db.Integer)
    hole2 = db.Column(db.Integer)
    hole3 = db.Column(db.Integer)
    hole4 = db.Column(db.Integer)
    hole5 = db.Column(db.Integer)
    hole6 = db.Column(db.Integer)
    hole7 = db.Column(db.Integer)
    hole8 = db.Column(db.Integer)
    hole9 = db.Column(db.Integer)
    hole10 = db.Column(db.Integer)
    hole11 = db.Column(db.Integer)
    hole12 = db.Column(db.Integer)
    hole13 = db.Column(db.Integer)
    hole14 = db.Column(db.Integer)
    hole15 = db.Column(db.Integer)
    hole16 = db.Column(db.Integer)
    hole17 = db.Column(db.Integer)
    hole18 = db.Column(db.Integer)


    def __init__(self, round_id, player_id, hole1, hole2, hole3, hole4, hole5, hole6, hole7, hole8, hole9, hole10, hole11, hole12, hole13, hole14, hole15, hole16, hole17, hole18):
        self.round_id = round_id
        self.player_id = player_id
        self.hole1 = hole1
        self.hole2 = hole2
        self.hole3 = hole3
        self.hole4 = hole4
        self.hole5 = hole5
        self.hole6 = hole6
        self.hole7 = hole7
        self.hole8 = hole8
        self.hole9 = hole9
        self.hole10 = hole10
        self.hole11 = hole11
        self.hole12 = hole12
        self.hole13 = hole13
        self.hole14 = hole14
        self.hole15 = hole15
        self.hole16 = hole16
        self.hole17 = hole17
        self.hole18 = hole18



class Roundinprogress(db.Model):
    token = db.Column(db.String(42), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    timestamp = db.Column(db.DateTime, default=datetime.now)
    created_by_player_id = db.Column(db.Integer, db.ForeignKey('player.id'))

    def __init__(self, course_id, token, created_by_player_id):
        self.course_id = course_id
        self.created_by_player_id = created_by_player_id
        self.token = token

    def __repr__(self):
        return '<Round %r>' % self.id



class Scorerequest(db.Model):
    roundinprocess_token = db.Column(db.String(42), db.ForeignKey('roundinprogress.token'), primary_key=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    invited_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)


    def __init__(self, roundinprocess_token, inviter_id, invited_id):
        self.roundinprocess_token = roundinprocess_token
        self.inviter_id = inviter_id
        self.invited_id = invited_id


class Scoreinprogress(db.Model):
    roundinprogress_token = db.Column(db.String(42), db.ForeignKey('roundinprogress.token'), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    hole1 = db.Column(db.Integer)
    hole2 = db.Column(db.Integer)
    hole3 = db.Column(db.Integer)
    hole4 = db.Column(db.Integer)
    hole5 = db.Column(db.Integer)
    hole6 = db.Column(db.Integer)
    hole7 = db.Column(db.Integer)
    hole8 = db.Column(db.Integer)
    hole9 = db.Column(db.Integer)
    hole10 = db.Column(db.Integer)
    hole11 = db.Column(db.Integer)
    hole12 = db.Column(db.Integer)
    hole13 = db.Column(db.Integer)
    hole14 = db.Column(db.Integer)
    hole15 = db.Column(db.Integer)
    hole16 = db.Column(db.Integer)
    hole17 = db.Column(db.Integer)
    hole18 = db.Column(db.Integer)

    def __init__(self, round_id, player_di):
        self.round_id = round_id
        self.player_id = player_id
