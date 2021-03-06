# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from pymongo import MongoClient
from config import config
import jwt
import datetime
import hashlib

from like import like
from auth import auth
from tour import tour

client = MongoClient(config["DB_URL"], 27017)
db = client.airtravel

app = Flask(__name__)
app.register_blueprint(tour, url_prefix="/tour")
app.register_blueprint(like, url_prefix="/like")
app.register_blueprint(auth, url_prefix="/auth")


@app.route("/")
def home():
    user_token = request.cookies.get("mytoken")
    user_nickname = ""
    user_info = ""
    user_own = 0
    if user_token is not None:
        payload = jwt.decode(user_token, config["SECRET_KEY"], algorithms=["HS256"])
        user_info = db.user.find_one({"user_id": payload["user_id"]}, {"_id": False})
        user_nickname = user_info["nick"]
    else:
        user_nickname = None
    tour_list = list(db.card.find({}))
    for tour in tour_list:
        tour["user_own"] = 0
        if user_info:
            user_like = db.like.find_one({"user_id": payload["user_id"], "card_id": tour["_id"]})
        tour["_id"] = str(tour["_id"])
        if user_info:
            if tour["author_id"] == user_info["user_id"]:
                tour["user_own"] = 1
            else:
                tour["user_own"] = 0
            if user_like is not None:
                tour["user_like"] = 1
            else:
                tour["user_like"] = 0
    return render_template("index.html", lists=tour_list, userNickName=user_nickname)


@app.route("/mytour", methods=["GET"])
def getTourByUser():
    token_receive = request.cookies.get("mytoken")
    user_info = ""
    if token_receive is None:
        return ({"result": "fail", "msg": "로그인을 해주세요"})
    else: 
        payload = jwt.decode(token_receive, config["SECRET_KEY"], algorithms=["HS256"])
        user_info = db.user.find_one({"user_id": payload["user_id"]}, {"_id": False})

        tour_list = list(db.card.find({"author_id": payload["user_id"]}))

        for tour in tour_list:
            if user_info:
                user_like = db.like.find_one({"user_id": payload["user_id"], "card_id": tour["_id"]})
            tour["_id"] = str(tour["_id"])
            if user_info:
                if user_like is not None:
                    tour["user_like"] = 1
                else:
                    tour["user_like"] = 0
        return render_template("mypage.html", lists=tour_list)


if __name__ == "__main__":
    app.run("0.0.0.0", port=5050, debug=True)