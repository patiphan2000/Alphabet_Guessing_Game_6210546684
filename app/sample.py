from flask import Flask, request, jsonify, redirect
from pymongo import MongoClient
import os, json, redis
import string
import random

# App
application = Flask(__name__)

# connect to MongoDB
mongoClient = MongoClient('mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_AUTHDB'])
db = mongoClient[os.environ['MONGODB_DATABASE']]

# connect to Redis
redisClient = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=os.environ.get("REDIS_PORT", 6379), db=os.environ.get("REDIS_DB", 0))

@application.route('/')
def index():
    x = db["game"]
    body = "<h1>MongoDB Exercise</h1>"
    body += "<h2>Alphabet Guessing Game</h2>"
    body += "<h3>By Patiphan Srichai 6210546684</h3>"
    body += """Choose: <input type="submit" name="questioning[]" value="Start" onclick="location.href='/start'" />"""
    return body

@application.route('/start')
def start():
    start = db.game.find_one({"game_start": True})
    if (start):
        return redirect("/play")
    else:
        answers = []
        for i in range(4):
            answers.append(random.choice(string.ascii_uppercase[:4]))
        db.game.insert_one({
            "question": ["_", "_", "_", "_"],
            "answer": answers,
            "guessing": [],
            "fail": 0,
            "correct": 0,
            "game_start": True,
        })
        return redirect("/play")

@application.route('/play')
def play():
    game = db.game.find_one({"game_start": True})

    if not game:
        return redirect("/start")

    choice = request.args.get('answer')

    if game["correct"] >= 4:
        db.game.update_one({"game_start": True}, {"$set": {"game_start": False}})
        return redirect("/gameover")

    if (choice):
        correct = game["correct"]
        if (choice == game["answer"][correct]):
            db.game.update_one({"game_start": True}, {"$inc": {"correct": 1}})

            db.game.update_one({"game_start": True}, {"$push": {"guessing": str(choice)}})
            new_question = db.game.find_one({"game_start": True})["guessing"]
            for i in range(4 - len(new_question)):
                new_question.append("_")
            db.game.update_one({"game_start": True}, {"$set": {"question": new_question}})
        else:
            db.game.update_one({"game_start": True}, {"$inc": {"fail": 1}})
        return redirect("/play")
    else:
        body = "<h1>MongoDB Exercise</h1>"
        body += "<h2>Alphabet Guessing Game</h2>"
        result = game["question"]

        body += '<span style="padding-left: 5px">'
        for r in result:
            body += r + " "
        body += "</span>"

        body += "</br></br>"
        body += '<span>'
        body += """<input type="submit" value="A" onclick="location.href='/play?answer=A'" style="margin-left: 5px"/>"""
        body += """<input type="submit" value="B" onclick="location.href='/play?answer=B'" style="margin-left: 5px"/>"""
        body += """<input type="submit" value="C" onclick="location.href='/play?answer=C'" style="margin-left: 5px"/>"""
        body += """<input type="submit" value="D" onclick="location.href='/play?answer=D'" style="margin-left: 5px"/>"""
        body += "</span>"

        body += "</br></br>"
        body += "fail:  " + str(game["fail"])

        body += "</br></br>"
        body += """<input type="submit" name="questioning[]" value="I'm give up bro" onclick="location.href='/giveup'" />"""

        return body

    return """<h1>Play</h1></br><input type="submit" name="questioning[]" value="A" onclick="location.href='/play?answer=A'" />"""

@application.route('/gameover')
def game_over():
    game = db.game.find_one({"game_start": False})
    body = ""
    if game["correct"] >= 4:
        body = "<h1>You win!!</h1>"
    else:
        body = "<h1>Game Over</h1>"
    body += "<h2>The answer is : "
    for i in range(4):
        body += game["answer"][i] + " "
    body += "</h2>"
    body += "<h3>you failed " + str(game["fail"]) + " times</h3>"

    body += "</br>"
    game = db.game.delete_one({"game_start": False})
    body += """<input type="submit" name="questioning[]" value="Play again" onclick="location.href='/start'" />"""

    return body

@application.route('/giveup')
def give_up():
    db.game.update_one({"game_start": True}, {"$set": {"game_start": False}})
    return redirect("/gameover")

@application.route('/sample')
def sample():
    doc = db.test.find_one()
    # return jsonify(doc)
    body = '<div style="text-align:center;">'
    body += '<h1>Python</h1>'
    body += '<p>'
    body += '<a target="_blank" href="https://flask.palletsprojects.com/en/1.1.x/quickstart/">Flask v1.1.x Quickstart</a>'
    body += ' | '
    body += '<a target="_blank" href="https://pymongo.readthedocs.io/en/stable/tutorial.html">PyMongo v3.11.2 Tutorial</a>'
    body += ' | '
    body += '<a target="_blank" href="https://github.com/andymccurdy/redis-py">redis-py v3.5.3 Git</a>'
    body += '</p>'
    body += '</div>'
    body += '<h1>MongoDB</h1>'
    body += '<pre>'
    body += json.dumps(doc, indent=4)
    body += '</pre>'
    res = redisClient.set('Hello', 'World')
    if res == True:
      # Display MongoDB & Redis message.
      body += '<h1>Redis</h1>'
      body += 'Get Hello => '+redisClient.get('Hello').decode("utf-8")
    return body

if __name__ == "__main__":
    ENVIRONMENT_DEBUG = os.environ.get("FLASK_DEBUG", True)
    ENVIRONMENT_PORT = os.environ.get("FLASK_PORT", 5000)
    application.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)