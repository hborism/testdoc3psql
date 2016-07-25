import os
import uuid
import datetime
from flask import Flask
from flask import request, render_template, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import exc
from werkzeug.utils import secure_filename

info= {"header":"Social golf app by Axel and Boris" ,"body": "An app developed for further enhancing the experience of the wonderful game of golf"}
henrik={"id":1, "firstName": "Henrik", "lastName": "Boris-Möller", "hcp": 8.8, "club": "Wasa GK"}
axel = {"id":2, "firstName": "Axel", "lastName": "Sundberg", "hcp": 4.8, "club": "Båstad GK"}
card= {"id":1, "course":"LAGK", "timestamp": "14.30 2016-06-12", "score": {1:None, 2:None, 3:None}, "ForImprovementInfo":"Instead of score:(...) we will in the future have (player1:((playerId:1... (score: () etc"}

UPLOAD_FOLDER = '/usr/src/app/profilepictures'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{db_user}:{db_password}@{db_service}:{db_port}/{db_name}
app.config['UPLOAD_FOLDER'] = '/usr/src/app/profilepictures'


db = SQLAlchemy(app)



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
        return '<Club %r>' % self.name



class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(40))
    email = db.Column(db.String(120), unique=True)
    hcp = db.Column(db.Integer)
    profile_picture_id = db.Column(db.String(36), unique=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))

    def __init__(self, first_name, last_name, email, hcp, profile_picture_id, club_id):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hcp = hcp
        self.profile_picture_id = profile_picture_id
        self.club_id = club_id

    def __repr__(self):
        return '<Player %r>' % self.email



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



'''
--------------------------------------------
 ____   ___  _   _ _____ ___ _   _  ____
|  _ \ / _ \| | | |_   _|_ _| \ | |/ ___|
| |_) | | | | | | | | |  | ||  \| | |  _
|  _ <| |_| | |_| | | |  | || |\  | |_| |
|_| \_\\___/ \___/  |_| |___|_| \_|\____|
--------------------------------------------
'''

# @app.route('/upload', methods=['GET', 'POST'])
# def upload():
#     # if request.method == 'POST':
#         # file = request.files['file']
#         # extension = os.path.splitext(file.filename)[1]
#         # f_name = str(uuid.uuid4()) + extension
#         # file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
#         # return json.dumps({'filename':f_name})
#     return "use POST request"
#
# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


'''
UPLOAD PICTURE
work in progress. currently only possible to upload via the html page
'''
@app.route('/uploadpic', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # return redirect(url_for('upload_file', filename=filename))
            return "uploaded :)"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

'''
GET PICTURE
get the picture of specific name (including .jpg or .png etc)
'''
@app.route('/picture/<pictureId>')
def get_pitcure(pictureId):
	try:
		filename='profilepictures/'+str(pictureId)
		return send_file(filename, mimetype='image')
	except FileNotFoundError:
		return jsonify({"error": {"message":"There exist no picture with that id", "type":"not found"}})



'''NEW CLUB
is done directly in database, ie no API for this function
'''


'''
NEW Course
is done directly in database, ie no API for this function
'''


'''
NEW PLAYER
JSONinput: first_name, last_name, email, hcp, club_id
JSONoutput: ---
'''
@app.route('/newplayer', methods=['POST'])
def newuser():
	newplayer=Player(request.json["first_name"], request.json["last_name"],request.json["email"],request.json["hcp"], None, request.json["club_id"])
	try:
		db.session.add(newplayer)
		db.session.commit()
		return ("Player entered into database"), 200
	except exc.IntegrityError:
		return "integrity error", 502




'''
NEW ROUND
JSONinput: course_id, player_id
JSONoutput: ---
'''
@app.route('/newround', methods=['POST'])
def newround():
    newround=Round(request.json['course_id'], request.json['player_id'])
    try:
        db.session.add(newround)
        db.session.commit()
        return "Round started and added to database", 200
    except exc.IntegrityError:
        return "integrity error", 502



'''
NEW SCORE
JSONinput: round_id, player_id
JSONoutput: ---
'''
@app.route('/newscore', methods=['POST'])
def newscore():
    newscore=Score(request.json['round_id'], request.json['player_id'])
    try:
        db.session.add(newscore)
        db.session.commit()
        return "Score added", 200
    except exc.IntegrityError:
        return "integrity error", 502



'''
NEW SCOREHOLE
JSONinput: round_id, player_id, hole_id, shots
JSONoutput: ---------
'''
@app.route('/scorehole', methods=['POST'])
def scorehole():
    scorehole=ScoreHole(request.json['round_id'], request.json['player_id'], request.json['hole_no'], request.json['shots'])
    try:
        db.session.add(scorehole)
        db.session.commit()
        return "scorehole added", 200
    except exc.IntegrityError:
        return "integrity error", 502








#-----------------------------OLD stuff: replace with functions using psql database----------------------------

@app.route('/', methods=['GET'])
def index():
    return jsonify({"info":info})

@app.route("/user/<int:userId>")
def user(userId):
	if userId==1:
		return jsonify({"userInfo":henrik})
	if userId==2:
		return jsonify({"userInfo":axel})
	else:
		return jsonify({"error": {"message":"There exist no user with that id", "type":"not found"}})

@app.route("/scorecard/<int:scoreCardId>", methods=['GET'])
def scoreCard(scoreCardId):
	if scoreCardId==1:
		return jsonify({"scoreCard":card})
	else:
		return jsonify({"error": {"message":"There exist no round with that id", "type":"not found"}})


@app.route("/scorecard/<int:scoreCardId>", methods=['POST'])
def addScore(scoreCardId):
	if scoreCardId==1:
		hole=request.json["hole"]
		score=request.json["score"]
		if hole>3 or hole<1:
			return jsonify({"error": {"message":"There exist no hole with that id", "type":"not found"}})
		card["score"][hole]=score
		return jsonify({"hole":hole, "score":score})
	else:
		return jsonify({"error": {"message":"There exist no round with that id", "type":"not found"}})


if __name__ == '__main__':
    app.run()
