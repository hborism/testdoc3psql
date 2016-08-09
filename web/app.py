import sqlalchemy
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



import os
import uuid
import datetime
import urllib.request
import json
from flask import Flask
from flask import request, render_template, jsonify, send_file, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import exc
from werkzeug.utils import secure_filename

info= {"status":200, "header":"Social golf app by Axel and Boris" ,"body": "An app developed for further enhancing the experience of the wonderful game of golf"}
henrik={"id":1, "firstName": "Henrik", "lastName": "Boris-Möller", "hcp": 8.8, "club": "Wasa GK"}
axel = {"id":2, "firstName": "Axel", "lastName": "Sundberg", "hcp": 4.8, "club": "Båstad GK"}
card= {"id":1, "course":"LAGK", "timestamp": "14.30 2016-06-12", "score": {1:None, 2:None, 3:None}, "ForImprovementInfo":"Instead of score:(...) we will in the future have (player1:((playerId:1... (score: () etc"}

UPLOAD_FOLDER = '/usr/src/app/profilepictures'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@postgres:5432/postgres'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{db_user}:{db_password}@{db_service}:{db_port}/{db_name}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['UPLOAD_FOLDER'] = '/usr/src/app/profilepictures'


db = SQLAlchemy(app)


from models import *

'''
--------------------------------------------
 ____   ___  _   _ _____ ___ _   _  ____
|  _ \ / _ \| | | |_   _|_ _| \ | |/ ___|
| |_) | | | | | | | | |  | ||  \| | |  _
|  _ <| |_| | |_| | | |  | || |\  | |_| |
|_| \_\\___/ \___/  |_| |___|_| \_|\____|
--------------------------------------------
'''

'''---------------------------------------------------------------------------
ERRORS
'''

@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error":'unknown 404-error', "message":"unknown reason. Please check backend", "status":404}), 404

@app.errorhandler(501)
def page_not_found(e):
    return jsonify({"error":'unknown 501-error', "message":"unknown reason. Please check backend", "status":510}), 510

@app.errorhandler(502)
def page_not_found(e):
    return jsonify({"error":'unknown 502-error', "message":"unknown reason. Please check backend", "status":510}), 510

@app.errorhandler(503)
def page_not_found(e):
    return jsonify({"error":'unknown 503-error', "message":"unknown reason. Please check backend", "status":510}), 510

@app.errorhandler(504)
def page_not_found(e):
    return jsonify({"error":'unknown 504-error', "message":"unknown reason. Please check backend", "status":510}), 510

@app.errorhandler(500)
def page_not_found(e):
    return jsonify({"error":'unknown 500-error', "message":"unknown reason. Please check backend", "status":510}), 510

'''-----------------------------------------------------------------------------
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


'''----------------------------------------------------------------------------
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



'''----------------------------------------------------------------------------------
LOGIN WITH EMAIL
JSONinput: email, password
JSONoutput: backend access token
'''
@app.route('/loginwithemail', methods=['POST'])
def loginwithemail():
    email = request.json["email"]
    password = request.json["password"]
    player = Player.query.filter_by(email=email).first()
    if player is None:
        return jsonify({"error":"login failed", "message":"email does not exist", "status":400}), 400

    if (player.password == password):
        return jsonify({"access_token":player.access_token, "message":"login successful", "status":200}), 200
    else:
        return jsonify({"error":"login failed", "message":"email and password did not match", "status":401}), 401

'''----------------------------------------------------------------------------------------
REGISTER WITH EMAIL
JSONinput: first_name, last_name, hcp, club_id, password, email
JSONoutput:
'''
@app.route('/registerwithemail', methods=['POST'])
def registerwithemail():
    email = request.json["email"]
    password = request.json["password"]
    first_name = request.json["first_name"]
    last_name = request.json["last_name"]
    hcp = request.json["hcp"]
    club_name = request.json["club_name"]

    player = Player.query.filter_by(email=email).first()
    if player is not None:
        return jsonify({"error":"user with that email aldready exists", "message":"please enter another email or login", "status":400}),400
    else:
        return createPlayer(first_name, last_name, email, hcp, None, None, club_name, password, None)

'''----------------------------------------------------------------------------
CREATEPLAYER
'''
#need to add friends later!!!
def createPlayer(first_name, last_name, email, hcp, profile_picture_id, cover_picture_id, club_name, password, friends):
    access_token = generateAccessToken()
    newplayer=Player(first_name, last_name, email, hcp, profile_picture_id, cover_picture_id, club_name, access_token, password)
    try:
        db.session.add(newplayer)
        db.session.commit()
        return jsonify({"message":"Player added successfully to the database","access_token":newplayer.access_token, "status":200}), 200
    except exc.IntegrityError:
        return jsonify({"error":"serverside error", "message":"Could not add player to database", "status":500}), 500


'''-----------------------------------------------------------------------------
GENERATE ACCESSTOKEN
'''
def generateAccessToken():
    access_token = str(uuid.uuid4())
    while Player.query.filter_by(access_token=access_token).first() is not None:
        access_token = str(uuid.uuid4())

    return access_token;



'''---------------------------------------------------------------------------
LOGIN WITH FACEBOOK
JSONinput: facebook access token
JSONoutput: backend access token
NOTCOMPLETE ORCHECKED!
'''
@app.route('/loginwithfacebook', methods=['POST'])
def loginwithfacebook():

    '''get facebook info'''
    facebookToken = request.json["access_token"]
    url="https://graph.facebook.com/me?fields=first_name,last_name,email,friends&access_token="+facebookToken
    try:
        resonse = urllib.request.urlopen(url)
        data=response.read().decode("utf-8")
        datajson=json.loads(data)
    except urllib.error.HTTPError:
        return "error", 400

    '''check to see if email is present in database
    if present then send back access token to give access
    if not present then create new player and issue access token'''
    player = Player.query.filter_by(email=datajson['email']).first()
    if player is not None:
        return jsonify({"access_token":player.access_token})
    else:
        #try and get facebook profile picture and save it. If fails then profile_picture_id is set to None
        try:
            picture=urllib.request.urlopen("https://graph.facebook.com/me/picture?height=400&width=400&type=normal&access_token="+facebookToken)
            profile_picture_id = str(uuid.uuid4())+".jpg"
            output= open("profilepictures/"+profile_picture_id, "wb")
            output.write(picture.read())
            output.close()
        except:
            profile_picture_id=None

        return createPlayer(datajson["first_name"], datajson["last_name"], datajson["email"], None, profile_picture_id, None, None, datajson["friends"])


'''------------------------------------------------------------------------------------
GET FREINDS
'''
@app.route('/getfriends', methods=['GET'])
def getFriends():
    a = db.aliased(Player, name='Player')
    token = request.headers.get('Access-token')
    playerList = Friend.query.join(Player, Friend.id2==Player.id).join(a, Friend.id1==a.id).add_columns(Player.id, Player.first_name, Player.last_name, Player.hcp, Player.club_name, Player.profile_picture_id, Player.cover_picture_id).filter(a.access_token == token).all()

    if not playerList:
        player = Player.query.filter_by(access_token=token).first()
        if player is None:
            return jsonify({"status":400, "error":"No player with that accesstoken", "message":"Please enter a valid access-token"}),400

    friends=[{"id":row.id, "first_name":row.first_name, "last_name":row.last_name, "hcp":row.hcp, "club_name":row.club_name, "profile_picture_id":row.profile_picture_id, "cover_picture_id":row.cover_picture_id} for row in playerList]
    return jsonify({"status":200, "friends":friends})



'''----------------------------------------------------------------------------------
GET CLUBS
'''
@app.route('/getclubs', methods=['GET'])
def getClubs():
    result = Club.query.order_by(Club.name).all()
    clubs=[row.serialize() for row in result]
    return jsonify({"status":200, "clubs":clubs})
        #return jsonify({"data":[{"hello":"bye","whatever":"cool"},{"key2":"one value"}]})
        # explanation here: http://stackoverflow.com/questions/7102754/jsonify-a-sqlalchemy-result-set-in-flask
        # and here: http://stackoverflow.com/questions/5022066/how-to-serialize-sqlalchemy-result-to-json




'''---------------------------------------------------------------------------
NEW FRIEND
'''


'''----------------------------------------------------------------------------
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



'''-------------------------------------------------------------------------------
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


'''-------------------------------------------------------------------------------
GET My INFO and UPDATe INFO
HEADERinput: Access-token
JSON: all info about oneself
'''
@app.route("/getmyprofileinfo")
def me():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    club=Club.query.filter_by(id=player.club_id).first()
    return jsonify({"first_name":player.first_name, "last_name":player.last_name, "hcp":player.hcp, "club_id":player.club_id, "club_name":club.name, "club_id":club.id, "email":player.email, "status":200}),200

'''-----------------------------------------------------------------------------
GET MY STATS
'''
@app.route("/getmystats")
def mystats():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    club=Club.query.filter_by(id=player.club_id).first()
    return jsonify({"avg_score": player.avg_score, "par_streak":player.par_streak, "birdie_streak":player.birdie_streak, "best_club": club.name, "best_club_id":club.id, "best_hole":player.best_hole})


'''----------------------------------------------------------------------------------
CHANGE HCP
'''
@app.route("/me/hcp", methods=['POST'])
def changeHCP():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()

    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    player.hcp = request.json["hcp"]
    db.session.commit()
    return jsonify({"message":"Success!", "new_hcp":player.hcp, "status":200}),200


'''--------------------------------------------------------------------------------
GET player info
'''
@app.route("/player/<int:player_id>")
def player(player_id):
    token=request.headers.get('Access-token')
    client_player=Player.query.filter_by(access_token=token).first()
    if client_player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "type":"not found", "status":400}),400

    friend = Friends.query.filter_by(id1=client_player.id,id2=player_id).first()

    if friend is None:
        return jsonify({"error":"Since you are not friend with player of that id you are now allowed to see the players info", "type":"not friend", "status":400}),400
    else:
        player=Player.query.filter_by(id=player_id).first()
        club=Club.query.filter_by(id=player.club_id).first()
        return jsonify({"first_name": player.first_name, "last_name":player.last_name, "hcp":player.hcp, "club_id":player.club_id, "club_name":club.name, "profile_picture_id":player.profile_picture_id, "status":200})




'''----------------------------------------------------------------------------------
CHECK IF friends

def getFriends(player_id):
    friends = Friends.query.filter_by(id1=player_id).all()
    return jsonify({"friends": friends})
'''


#-----------------------------OLD stuff: replace with functions using psql database----------------------------

@app.route('/', methods=['GET'])
def index():
    user= request.args.get('user')
    token = request.headers.get('Access-token')
    other = request.headers.get('otherkey')
    return jsonify({"info":info, "access token":token, "other key":other, "user":user})



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
