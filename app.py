from flask import Flask, session, request, url_for, redirect, render_template
from utils import users, userEvents, connect, tmEvents, directions1, wunderground, notifs
import datetime
app = Flask(__name__)
app.secret_key = "deal with this later"

#======================================================================================= ROOT
@app.route("/")
def root():
    if( 'username' in session.keys() ):
        return redirect(url_for( 'home' ))
    else:
        return redirect(url_for( 'login' ))
        
#====================================================================================== LOGIN
@app.route("/login/")
def login():
    if "username" in session:
        return redirect(url_for('home'))
    return render_template('login.html')

#======================================================================= AUTHENTICATING LOGIN
@app.route("/authenticate/", methods=['POST'])
def authenticate():
    print request.form.values()
    pw = request.form["password"]
    un = request.form["user"]
    em = request.form["email"]
    tp = request.form["account"]#login vs. register
    
    if tp == "Register":
        regRet = users.register(un,em,pw)#returns an error/success message
        return render_template('login.html', message = regRet)
        
    if tp == "Login":
        text = users.login(un,em,pw)#error message
        if text == "":#if no error message, succesful go back home
            session["username"] = un
            return redirect(url_for('home'))
        return render_template('login.html', message = text)

#============================================================= ALL EVENTS PAGE (AKA MAIN PAGE)
@app.route("/mainpage/")
def home():
    n = datetime.datetime.now()
    tmEvents.tmStartDT(n.year,n.month,n.day,n.hour)
    eventsArr = tmEvents.tmCall(session['username'])
    return render_template("main.html", user = session['username'], events=eventsArr)

#============================================================= SINGLE EVENTS PAGE
@app.route("/event/<id>/")
def event(id):
    info = tmEvents.eventInfo(id)
    zip = info["venue"]["zip"]
    state = info["venue"]["state"]
    if zip != "00000":
      wunderground.zipcode(zip)
    elif state != "":
      wunderground.location(state, info["venue"]["city"])
    else:
      return render_template("event.html", user = session['username'], event = info, weather = "Venue doesn't have enough information")
    return render_template("event.html", user = session['username'], event = info, weather = wunderground.wuCall(int(info["date"][0:4]),int(info["date"][5:7]),int(info["date"][8:10])))

#============================================================= GETTING DIRECTIONS TO EVENT
@app.route("/directions/<id>/")
def directions(id):
    info = tmEvents.eventInfo(id)
    return render_template("directions.html", event = info)


#======================================================== CREATING A HANGOUT EVENT (INIVITING)
@app.route("/filter/", methods=['POST'])
def filter():
    keyword=request.form['Keyword']
    if keyword != "":
        tmEvents.tmKeyword(keyword)
    pCode = request.form['Postal Code']
    if len(pCode)==5:
        tmEvents.tmCode(pCode)
    city = request.form['City']
    if city!="":
        tmEvents.tmCity(city)
    if 'When' in request.form:
        when = request.form['When']
        time = datetime.datetime.now()
        if when=="Week":
            add = datetime.timedelta(days=7)
            time = time+add
        else: #when=Two Weeks
            add = datetime.timedelta(days=14)
            time = time+add
            print "TIME: " + str(time)
        tmEvents.tmStartDT(time.year, time.month, time.day, time.hour)
    return redirect( url_for('home') )

#==================joinEvent=================
@app.route("/joinEvent/<id>")
def joinEvent(id):
    userEvents.addEvent(session['username'], id)
    return redirect( url_for('home') )

#==================getDirections=================
@app.route("/getdirections/<id>", methods=['POST'])
def getDirections(id):
    event =  tmEvents.eventInfo(id)
    out = directions1.directionsCall(event['venue']['streetAddr'].replace(' ','+'),request.form['location'].replace(' ','+'), request.form['trans'])
    return render_template("event.html",event=event, directions= out)

#========================userProfile=======================
@app.route("/user/<user>/")
def userProfile(user):
    friendsDict = connect.listFriends(user)
    eventsDict = userEvents.listEvents(user)
    return render_template("profile.html", username=user, events=eventsDict, friends=friendsDict, email=users.getEmail(user))

@app.route("/user/")
def profile():
  return redirect(url_for('userProfile', user=session['username']))

#========================notifications===================
@app.route("/notifications/")
def notifications():
    msgs = notifs.getNotifs(session['username'])
    return render_template("notifications.html", notifs=msgs,rfriends=connect.findFriends(session['username']))

#========================addFriend======================
@app.route("/addConnect/<newC>")
def addConnect(newC):
    connect.addFriend(session['username'], newC)
    return redirect( url_for('notifications') )

#===================================================================================== LOGOUT
@app.route("/logout/")
def logout():
    session.pop('username')
    return redirect(url_for('root'))

if __name__ == "__main__":
    app.debug = True
    app.run()
