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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


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

'''--------------------------------------------------------------------------
ROOT
'''
@app.route('/', methods=['GET'])
def index():
    user= request.args.get('user')
    token = request.headers.get('Access-token')
    other = request.headers.get('otherkey')
    return jsonify({"info":info, "access token":token, "other key":other, "user":user})



'''---------------------------------------------------------------------------
ERRORS
'''
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error":'unknown 404-error', "message":"Please check URL", "status":404}), 404

@app.errorhandler(501)
def page_not_found(e):
    return jsonify({"error":'unknown 501-error', "message":"unknown reason. Please check backend", "status":511}), 511

@app.errorhandler(502)
def page_not_found(e):
    return jsonify({"error":'unknown 502-error', "message":"unknown reason. Please check backend", "status":512}), 512

@app.errorhandler(503)
def page_not_found(e):
    return jsonify({"error":'unknown 503-error', "message":"unknown reason. Please check backend", "status":513}), 513

@app.errorhandler(504)
def page_not_found(e):
    return jsonify({"error":'unknown 504-error', "message":"unknown reason. Please check backend", "status":514}), 514

@app.errorhandler(500)
def page_not_found(e):
    return jsonify({"error":'unknown 500-error', "message":"unknown reason. Please check backend", "status":510}), 510


'''---------------------------------------------------------------------------
UPLOAD PROFILE PICTURE
'''
@app.route('/uploadprofilepicture', methods=['POST'])
def uploadprofilepicture():
    token = request.headers.get('Access-token')
    return (token)


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
        return jsonify({"error":"serverside error", "message":"Could not add player to database. Does the club exist in the database?", "status":500}), 500


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


'''-------------------------------------------------------------------------------
GET My INFO and UPDATe INFO
HEADERinput: Access-token
JSON: all info about oneself
'''
@app.route("/getmyprofileinfo", methods=['GET'])
def me():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    return jsonify({"id":player.id, "first_name":player.first_name, "last_name":player.last_name, "hcp":player.hcp, "club_name":player.club_name, "email":player.email, "profile_picture_id":player.profile_picture_id, "cover_picture_id":player.cover_picture_id, "status":200}),200

'''-----------------------------------------------------------------------------
GET MY STATS
'''
@app.route("/getmystats", methods=['GET'])
def mystats():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    return jsonify({"status":200, "avg_score": player.avg_score, "par_streak":player.par_streak, "birdie_streak":player.birdie_streak, "best_club_name": player.best_club_name, "best_hole":player.best_hole})



'''-------------------------------------------------------------------------
GET CLUBS AND COURSES
'''
@app.route("/getclubsandcourses", methods=['GET'])
def getclubsandcourses():
    clubs = Club.query.order_by(Club.name).all()
    clubdata = []
    for club in clubs:
        courses= Course.query.filter_by(club_name=club.name).all()
        coursedata=[]
        for course in courses:
            holes=Hole.query.filter_by(course_id=course.id).all()
            coursedata.extend([{"id":course.id, "course_name":course.name, "holes":[hole.serialize() for hole in holes]}])

        clubdata.extend([{"info":club.info, "name":club.name, "logo_id": club.logo_id, "cover_picture_id":club.cover_picture_id, "courses":coursedata}])



    return jsonify({"status":200, "clubs_with_courses":clubdata})


'''--------------------------------------------------------------------------
START NEW ROUND
'''
@app.route("/startnewround", methods=['POST'])
def startnewround():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    course_id = request.json['course_id']
    type = request.json['type']

    if type == 1:
        newroundinprogress = Roundinprogress(course_id, player.id, type)
        db.session.add(newroundinprogress)
        db.session.commit()

        score_token = str(uuid.uuid4())
        while Scoreinprogress.query.filter_by(score_token=score_token).first() is not None:
            score_token = str(uuid.uuid4())

        newscoreinprogress = Scoreinprogress(newroundinprogress.id, player.id, player.id, score_token)


        db.session.add(newscoreinprogress)
        db.session.commit()
        return jsonify({"message":"New round added to database","roundinprogress_id":newroundinprogress.id, "player_id":newscoreinprogress.player_id, "marker_id":newscoreinprogress.marker_id, "status":200}), 200

    return jsonify({"error": "Type shall be 1", "message":"Currently backend only supports type=1", "status":401}),401



'''---------------------------------------------------------------------------
NEW SCORE REQUEST and GET SCORE REQUEST
'''
@app.route("/newscorerequest", methods=['POST', 'GET'])
def newscorerequest():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    if request.method == 'POST':

        roundinprogress_id = request.json['roundinprogress_id']
        round = Roundinprogress.query.filter_by(id=roundinprogress_id).first()
        if round is None:
            return jsonify({"error": "Access token does not match that of a round", "message":"null round", "status":401}),401

        if round.created_by_player_id != player.id:
            return jsonify({"error": "Access token does not match that of the creator of the round", "message":"denied access", "status":402}),402

        invited_id = request.json['invited_id']

        newscorerequest = Scorerequest(roundinprogress_id, player.id, invited_id)
        db.session.add(newscorerequest)
        db.session.commit()
        return jsonify({"message":"Score request added to database", "status":200}),200

    # if request.method=='GET':
    result=Scorerequest.query.filter_by(invited_id=player.id).all()
    scorerequests=[row.serialize() for row in result]
    return jsonify({"status":200, "scorerequests":scorerequests})

'''--------------------------------------------------------------------------
SCORE REQUEST RESPONSE
'''
@app.route("/scorerequestresponse", methods=['POST'])
def scorerequestresponse():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    roundinprogress_id = request.json['roundinprogress_id']
    scorerequest = Scorerequest.query.filter_by(roundinprogress_id=roundinprogress_id).filter_by(invited_id=player.id).first()
    if scorerequest is None:
        return jsonify({"error": "Access token does not match that of a request", "message":"null request", "status":401}),401

    if scorerequest.invited_id != player.id:
        return jsonify({"error": "Access token does not match that of the invited", "message":"denied access", "status":402}),402

    accept = request.json['accept']
    db.session.delete(scorerequest)

    if accept == False or accept is None:
        db.session.commit()
        return jsonify({"message":"scorerequest removed", "status":200}),200

    # if accept == true
    score_token = str(uuid.uuid4())
    while Scoreinprogress.query.filter_by(score_token=score_token).first() is not None:
        score_token = str(uuid.uuid4())

    newscoreinprogress = Scoreinprogress(scorerequest.roundinprogress_id, player.id, scorerequest.inviter_id, score_token)
    db.session.add(newscoreinprogress)
    db.session.commit()
    return jsonify({"message":"New score added to round","roundinprogress_id":scorerequest.roundinprogress_id, "player_id":newscoreinprogress.player_id, "marker_id":newscoreinprogress.marker_id, "status":200}), 200



'''---------------------------------------------------------------------------
UPDATe SCOREHOLE
'''
@app.route("/updatescorehole", methods=['POST'])
def updatescorehole():
    token = request.headers.get('Access-token')
    requestsender = Player.query.filter_by(access_token = token).first()
    roundinprogress_id = request.json['roundinprogress_id']
    player_id = request.json['player_id']
    hole = request.json['hole']
    score = request.json['score']
    if hole <=0 or hole >=19:
        return jsonify({"error": "hole must be an int and in range 1-18", "message":"fix it", "status":401}),401

    scoretoupdate = Scoreinprogress.query.filter_by(roundinprogress_id=roundinprogress_id).filter_by(player_id=player_id).first()
    if scoretoupdate is None:
        return jsonify({"error": "There exist no scoreinprogress with that player_id and roundinprogress_id", "message":"invite a player or create a round", "status":400}),400

    if requestsender.id != scoretoupdate.player_id and requestsender.id != scoretoupdate.marker_id:
        return jsonify({"error": "You must be the marker or the player to be able to update the ", "message":"please log in as player or marker", "status":402}),402

    if scoretoupdate.player_signature==True or scoretoupdate.marker_signature==True:
        return jsonify({"error": "Scorecard already signed by player or marker or both", "message":"Please unsign before enter score", "status":403}),403

    command="scoretoupdate.hole"+str(hole)+"=score"
    exec(command)
    db.session.commit()

    return jsonify({"status":200, "message":"score updated"})


'''--------------------------------------------------------------------------
GET ROUND WITH SCORE
'''
@app.route("/getroundwithscores", methods=['GET'])
def getroundwithscores():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no player with that access token. please login", "message":"not found", "status":400}),400

    roundinprogress_id=request.headers.get('Roundinprogress-id')

    roundinprogress = Roundinprogress.query.filter_by(id=roundinprogress_id).first()
    if roundinprogress is None:
        return jsonify({"error": "There exist no roundinprogress with that id", "message":"not found", "status":401}),401

    course = Course.query.filter_by(id = roundinprogress.course_id).first()
    result = Scoreinprogress.query.filter_by(roundinprogress_id = roundinprogress_id).all()
    scores=[row.serialize() for row in result]
    return jsonify({"status":200, "scores":scores, "roundinprogress_id": roundinprogress.id, "course_name": course.name, "club_name": course.club_name, "course_id": roundinprogress.course_id, "timestamp": roundinprogress.timestamp, "created_by_player_id": roundinprogress.created_by_player_id, "type": roundinprogress.type})

'''---------------------------------------------------------------------------
SIGN AS PLAYER
'''
@app.route("/signasplayer", methods=['POST'])
def signasplayer():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no player with that access token. please login", "message":"not found", "status":400}),400

    roundinprogress_id=request.json["roundinprogress_id"]

    score= Scoreinprogress.query.filter_by(roundinprogress_id = roundinprogress_id).filter_by(player_id=player.id).first()
    if score is None:
        return jsonify({"error": "The roundinprogress_id and player_id does not match any scoreinprogress", "message":"not found", "status":401}),401

    signature = request.json['signature']
    if signature is None:
        signature = False

    score.player_signature=signature
    db.session.commit()
    if signature==False:
        return jsonify({"message": "Score unsigned", "status":200}),400

    return checkifroundisfinished(roundinprogress_id)
    # return jsonify({"status":200, "message":"score signed as player"})

'''--------------------------------------------------------------------------
SIGN AS MARKER
'''
@app.route("/signasmarker", methods=['POST'])
def signasmarker():
    token = request.headers.get('Access-token')
    player=Player.query.filter_by(access_token=token).first()
    if player is None:
        return jsonify({"error": "There exist no user with that access token. please login", "message":"not found", "status":400}),400

    roundinprogress_id=request.json["roundinprogress_id"]
    player_id = request.json["player_id"]
    score= Scoreinprogress.query.filter_by(roundinprogress_id = roundinprogress_id).filter_by(player_id=player_id).first()
    if score is None:
        return jsonify({"error": "The roundinprogress_id and player_id does not match any scoreinprogress", "message":"not found", "status":401}),401

    if score.marker_id != player.id:
        return jsonify({"error": "The access-token does not belong to the marker of this score", "message":"invalid identification", "status":403}),403

    signature = request.json['signature']
    if signature is None:
        signature = False

    score.marker_signature=signature
    db.session.commit()
    if signature==False:
        return jsonify({"message": "Score unsigned", "status":200}),400

    return checkifroundisfinished(roundinprogress_id)
    # return jsonify({"status":200, "message":"score signed as marker"})


'''---------------------------------
CHECK IF ROUNDINPROGRESS IS SIGNED BY ALL

make sure to do this as one transaction so that not two people sign at the
same time and (finishing the round) and this function does not transfer
roundinprogress to round. Small risk that it would happen but if would be very annoying when it does
'''
def checkifroundisfinished(roundinprogress_id):
    scores = Scoreinprogress.query.filter_by(roundinprogress_id=roundinprogress_id).all()

    for score in scores:
        if score.player_signature==False or score.marker_signature==False:
            return jsonify({"status":201, "message":"score signed. Waiting for other to sign "})


    archiveround(scores, roundinprogress_id)
    return jsonify({"status":210, "message":"score signed. Everyone has signed. All ok "}), 210


'''-----------------------------
Archive round
'''
def archiveround(scores, roundinprogress_id):

    roundinprogress = Roundinprogress.query.filter_by(id=roundinprogress_id).first()

    round = Round(roundinprogress.course_id, roundinprogress.created_by_player_id, roundinprogress.type)
    db.session.add(round)
    db.session.commit()

    for s in scores:
        archivescore = Score(round.id, s.player_id, s.marker_id, s.hole1, s.hole2, s.hole3, s.hole4, s.hole5, s.hole6, s.hole7, \
        s.hole8, s.hole9, s.hole10, s.hole11, s.hole12, s.hole13, s.hole14, s.hole15, s.hole16, s.hole17, s.hole18)
        db.session.add(archivescore)
        db.session.delete(s)

    # check that there are no dependencies in scorerequest. If there are, then delete
    requests = Scorerequest.query.filter_by(roundinprogress_id = roundinprogress_id)
    for r in requests:
        db.session.delete(r)

    db.session.commit()

    db.session.delete(roundinprogress)
    db.session.commit()
    return None


if __name__ == '__main__':
    app.run()
