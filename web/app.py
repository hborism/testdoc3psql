import os
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
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = SQLAlchemy(app)


#-----------------------------DATABASEMODEL------------------------------

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    # players = db.relationship('Player', backref='club', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Club %r>' % self.name

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(30))
    lastName = db.Column(db.String(40))
    email = db.Column(db.String(120), unique=True)
    hcp = db.Column(db.Integer)
    clubId = db.Column(db.Integer, db.ForeignKey('club.id'))

    def __init__(self, firstName, lastName, email, hcp, clubId):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.hcp = hcp
        self.clubId = clubId

    def __repr__(self):
        return '<Player %r>' % self.email

# class Course(db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	name = db.Column(db.String(40))
# 	numberOfHoles = db.Column(db.Integer)
# 	clubId= db.Column(db.Integer, db.ForeignKey(club.id))

# 	def __init__(self, name, numberOfHoles, clubId)
# 		self.name = name
# 		self.numberOfHoles = numberOfHoles
# 		self.clubId = clubId

# 	def __repr__(self):
# 		return '<Course'

#-------------------------------ROUTING-----------------------------------


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # if request.method == 'POST':
        # file = request.files['file']
        # extension = os.path.splitext(file.filename)[1]
        # f_name = str(uuid.uuid4()) + extension
        # file.save(os.path.join(app.config['UPLOAD_FOLDER'], f_name))
        # return json.dumps({'filename':f_name})
    return "use POST request"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploadpic', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':

    	if ('file' in request.files):
    		return "true"
    	return "false"

        # # check if the post request has the file part
        # if 'file' not in request.files:           
        #     return 'No file part'
        # file = request.files['file']
        # # if user does not select file, browser also
        # # submit a empty part without filename
        # if file.filename == '':
        #     return 'No selected file'
        # if file and allowed_file(file.filename):
        #     filename = secure_filename(file.filename)
        #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #     # return redirect(url_for('upload_file', filename=filename))
        #     return "uploaded :)"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

@app.route('/picture/<int:userId>')
def get_pitcure(userId):
	try:
		filename='profilepictures/'+str(userId)+'.jpg'
		return send_file(filename, mimetype='image')
	except FileNotFoundError:
		return jsonify({"error": {"message":"There exist no picture with that id", "type":"not found"}})



@app.route('/newuser', methods=['POST'])
def newuser():
	newplayer=Player(request.json["firstName"], request.json["lastName"],request.json["email"],request.json["hcp"],request.json["clubId"])

	try: 
		db.session.add(newplayer)
		db.session.commit()
		return ("Player entered into database")
	except exc.IntegrityError:
		return "integrity error"

	# newclub=Club("Lunds Akademiska golfklubb")
	# newplayer=Player("Henrik", "Boris-Möller", "henrik.borismoller@gmail.com", 88, 1)
	# db.session.add(newclub)
	# db.session.add(newplayer)

	# try:
	# 	db.session.commit()
	# 	return "Hej new player and club:)"
	# except exc.IntegrityError:
	# 	return "Integrity error. did mail already exist?"


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