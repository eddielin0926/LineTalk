import json
import os
import sys

from flask import Flask, jsonify, request, abort, send_file, render_template
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


class System():
    def __init__(self):
        self.users = []
        self.waiting = []
        self._id = 0

    def find_user(self, line_id):
        return next(filter(lambda x: x.line_id == line_id, self.users), None)

    def new_user(self, line_id):
        machine = TocMachine(
            system=self,
            id=self._id,
            line_id=line_id,
            states=["user", "intro", "intro_nickname",
                    "intro_gender", "intro_age", "preference", "prefered_gender", "prefered_age",
                    "pairing", "chating", "RPS", "waiting_RPS"],
            transitions=[
                {
                    "trigger": "advance",
                    "source": "user",
                    "dest": "user",
                    "conditions": "show_menu",
                },
                {
                    "trigger": "advance",
                    "source": "user",
                    "dest": "intro",
                    "conditions": "is_going_to_intro",
                },
                {
                    "trigger": "advance",
                    "source": "intro",
                    "dest": "user",
                    "conditions": "set_intro",
                },
                {
                    "trigger": "advance",
                    "source": "intro",
                    "dest": "intro_nickname",
                    "conditions": "is_going_to_intro_nickname",
                },
                {
                    "trigger": "advance",
                    "source": "intro_nickname",
                    "dest": "intro",
                    "conditions": "set_intro_nickname",
                },
                {
                    "trigger": "advance",
                    "source": "intro",
                    "dest": "intro_gender",
                    "conditions": "is_going_to_intro_gender",
                },
                {
                    "trigger": "advance",
                    "source": "intro_gender",
                    "dest": "intro",
                    "conditions": "set_intro_gender",
                },
                {
                    "trigger": "advance",
                    "source": "intro",
                    "dest": "intro_age",
                    "conditions": "is_going_to_intro_age",
                },
                {
                    "trigger": "advance",
                    "source": "intro_age",
                    "dest": "intro",
                    "conditions": "set_intro_age",
                },
                {
                    "trigger": "advance",
                    "source": "user",
                    "dest": "preference",
                    "conditions": "is_going_to_preference",
                },
                {
                    "trigger": "advance",
                    "source": "preference",
                    "dest": "user",
                    "conditions": "set_preference",
                },
                {
                    "trigger": "advance",
                    "source": "preference",
                    "dest": "prefered_age",
                    "conditions": "is_going_to_prefered_age",
                },
                {
                    "trigger": "advance",
                    "source": "prefered_age",
                    "dest": "preference",
                    "conditions": "set_prefered_age",
                },
                {
                    "trigger": "advance",
                    "source": "preference",
                    "dest": "prefered_gender",
                    "conditions": "is_going_to_prefered_gender",
                },
                {
                    "trigger": "advance",
                    "source": "prefered_gender",
                    "dest": "preference",
                    "conditions": "set_prefered_gender",
                },
                {
                    "trigger": "advance",
                    "source": "user",
                    "dest": "pairing",
                    "conditions": "is_going_to_pairing",
                },
                {
                    "trigger": "advance",
                    "source": "pairing",
                    "dest": "user",
                    "conditions": "cancel_pairing",
                },
                {
                    "trigger": "has_paired",
                    "source": "pairing",
                    "dest": "chating",
                },
                {
                    "trigger": "advance",
                    "source": "chating",
                    "dest": "chating",
                    "conditions": "call_bot",
                },
                {
                    "trigger": "advance",
                    "source": "chating",
                    "dest": "chating",
                    "conditions": "talking",
                },
                {
                    "trigger": "advance",
                    "source": "chating",
                    "dest": "RPS",
                    "conditions": "is_going_to_RPS",
                },
                {
                    "trigger": "advance",
                    "source": "RPS",
                    "dest": "waiting_RPS",
                    "conditions": "is_going_to_waiting_RPS",
                },
                {
                    "trigger": "advance",
                    "source": ["RPS", "waiting_RPS"],
                    "dest": "chating",
                    "conditions": "cancel_RPS",
                },
                {
                    "trigger": "advance",
                    "source": "chating",
                    "dest": "chating",
                    "conditions": "reject_RPS",
                },
                {
                    "trigger": "finish_RPS",
                    "source": ["RPS", "waiting_RPS"],
                    "dest": "chating",
                },
                {
                    "trigger": "advance",
                    "source": "waiting_RPS",
                    "dest": "waiting_RPS",
                    "conditions": "waiting_and_talking",
                },
                {
                    "trigger": "advance",
                    "source": ["chating", "waiting_RPS"],
                    "dest": "user",
                    "conditions": "leaving",
                },
                {
                    "trigger": "leave_chat",
                    "source": "chating",
                    "dest": "user",
                },
            ],
            initial="user",
            auto_transitions=False,
            show_conditions=True,
        )
        self.users.append(machine)
        self._id += 1
        return machine

    def pair(self, user):
        if not self.waiting:
            self.waiting.append(self.find_user(user.line_id))
            return False
        else:
            paired_user = self.waiting.pop(0)
            send_text_message(user.line_id, "配對成功!\n開始與對方聊天吧~\n輸入 @bot 呼叫選單")
            send_text_message(
                user.line_id, f"對方資訊\n暱稱: {'(未設定)' if not paired_user.nickname else paired_user.nickname}\n性別: {'(未設定)' if not paired_user.gender else paired_user.gender}\n年齡: {'(未設定)' if not paired_user.age else paired_user.age}")
            send_text_message(paired_user.line_id, "配對成功!\n開始與對方聊天吧~\n輸入 @bot 呼叫選單")
            send_text_message(
                paired_user.line_id, f"對方資訊\n暱稱: {'(未設定)' if not user.nickname else user.nickname}\n性別: {'(未設定)' if not user.gender else user.gender}\n年齡: {'(未設定)' if not user.age else user.age}")
            user.paired_user = paired_user
            paired_user.paired_user = user
            user.has_paired()
            paired_user.has_paired()
            app.logger.info(
                f"Paired user '{user.line_id}' and user '{paired_user.line_id}'")
            return True

    def cancel_pair(self, user):
        self.waiting = [x for x in self.waiting if not x.id == user.id]

    def leave(self, user):
        if user.paired_user:
            paired_user = user.paired_user
            user.paired_user = None
            paired_user.paired_user = None
            send_text_message(paired_user.line_id, "對方離開了聊天室😥")
            paired_user.leave_chat()

    def finished_RPS(self, user):
        paired_user = user.paired_user
        if not paired_user.RPS:
            return
        if (user.RPS == '剪刀✌' and paired_user.RPS == '布🖐') or (user.RPS  == '石頭👊' and paired_user.RPS == '剪刀✌') or (user.RPS  == '布🖐' and paired_user.RPS == '石頭👊'):
            send_text_message(user.line_id, f"對方出了{paired_user.RPS}，你贏了!")
            send_text_message(paired_user.line_id, f"對方出了{user.RPS}，你輸了!")
        elif (user.RPS == '剪刀✌' and paired_user.RPS == '剪刀✌') or (user.RPS  == '石頭👊' and paired_user.RPS == '石頭👊') or (user.RPS  == '布🖐' and paired_user.RPS == '布🖐'):
            send_text_message(user.line_id, f"對方出了{paired_user.RPS}，平手!")
            send_text_message(paired_user.line_id, f"對方出了{user.RPS}，平手!")
        elif (user.RPS == '剪刀✌' and paired_user.RPS == '石頭👊') or (user.RPS  == '石頭👊' and paired_user.RPS == '布🖐') or (user.RPS  == '布🖐' and paired_user.RPS == '剪刀✌'):
            send_text_message(user.line_id, f"對方出了{paired_user.RPS}，你輸了!")
            send_text_message(paired_user.line_id, f"對方出了{user.RPS}，你贏了!")
        user.RPS = None
        paired_user.RPS = None
        user.finish_RPS()
        paired_user.finish_RPS()

system = System()

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=event.message.text)
        )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(
        f"Request body: {json.dumps(json.loads(body), indent=2, sort_keys=True)}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        user_id = event.source.user_id
        user = system.find_user(user_id)
        if user == None:
            user = system.new_user(user_id)
            print("new user:", user_id)
        response = user.advance(event)
        if response == False:
            send_text_message(event.source.user_id, "請輸入「@bot」呼叫選單")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    if system.users:
        system.users[0].machine.get_graph().draw(
            "fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
