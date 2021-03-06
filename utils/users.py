#!/usr/bin/python

from hashlib import sha1
from sqlite3 import connect
from os import urandom

f = "data/hangout.db"

"""
TEXT username, TEXT email, TEXT salt, TEXT pass, TEXT eventIdList, TEXT types
"""

def login(user, email, password):
    db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM users WHERE username=?")
    sel = ""
    try:
        sel = c.execute(query,(user,))
    except:
        c.execute("CREATE TABLE users (username TEXT, email TEXT, salt TEXT, password TEXT, imgLink TEXT, eventIdList TEXT, types TEXT)")
        sel = c.execute(query,(user,));
    
    #records with this username
    #so should be at most one record (in theory)
    for record in sel:
        password = sha1(password+record[2]).hexdigest()#record[2] is the salt
        if (password==record[3]):
            return ""#no error message because it will be rerouted to mainpage
        else:
            return "User login has failed. Invalid password"#error message
    db.commit()
    db.close()
    return "Username does not exist"#error message

def getEmail(user):
    db = connect(f)
    c = db.cursor()
    query = "SELECT email FROM users WHERE username=?"
    sel = c.execute(query, (user,))
    for email in sel:
        return email[0]

def register(user, email, password):
    db = connect(f)
    c = db.cursor()
    try: #does table already exist?
        c.execute("SELECT * FROM users")
    except: #if not, this is the first user!
        c.execute("CREATE TABLE users (username TEXT, email TEXT, salt TEXT, password TEXT, eventIdList TEXT, types TEXT)")
    db.commit()
    db.close()
    return regMain(user, email, password)#register helper

def regMain(user, email, password):#register helper
    db = connect(f)
    c = db.cursor()
    reg = regReqs(user, email, password)
    if reg == "": #if error message is blank then theres no problem, update database
        salt = urandom(10).encode('hex')
        query = ("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)")
        password = sha1(password + salt).hexdigest()
        c.execute(query, (user, email, salt, password, "", ""))
        db.commit()
        db.close()
        return "Account created!"
    db.commit()
    db.close()
    return reg #return error message
        
def regReqs(user, email, password):      #error message generator
    if len(password) < 8 or len(password) > 32:
        return "Password must be 8-32 characters"
    if duplicate(user,email):  #checks if username already exists
        return "Username or email already exists"
    if " " in user or " " in password:
        return "Spaces not allowed in user or password"
    if user==password:
        return "Username and password must be different"
    return ""

def duplicate(user,email):#checks if username already exists
    db = connect(f)
    c = db.cursor()
    query = ("SELECT * FROM users WHERE username=? OR email=?")
    sel = c.execute(query, (user,email))
    retVal = False
    for record in sel:
        retVal = True
    db.commit()
    db.close()
    return retVal

def changePass(user,oldPss,newPass):
    db = connect(f)
    c = db.cursor
    query = "SELECT * FROM users WHERE username=?"
    sel = c.execute(query, (user,))
    for record in sel:
        if sha1(oldPass+record[2]).hexdigest() == record[3]:
	    query = "UPDATE users SET pass=? WHERE usernamen=?"
	    c.execute(query, (sha1(newPass+record[2]).hexdigest(), user))
	    return "Password was changed successfully"
	else:
	    return "Incorrect password entered"
    db.commit()
    db.close()
    return "Username does not exist"
