import random

from linebot.models import messages
from transitions.extensions import GraphMachine

from utils import send_button_message, send_text_message, send_confirm_message


topic_list = ['你喜歡運動嗎?', '最近有什麼讓你開心的事情嗎?', '你喜歡什麼類型的人?', '你最近有看甚麼電影嗎?', '你喜歡吃什麼呢?', '你有什麼興趣嗎?', '你喜歡旅行嗎?', '你有去過什麼國家?', '你是哪裡人啊?']

class TocMachine(GraphMachine):
    def __init__(self, system, id, line_id, **machine_configs):
        self.system = system
        self.id = id
        self.line_id = line_id
        self.machine = GraphMachine(model=self, **machine_configs)
        self.nickname=""
        self.gender=""
        self.age=""
        self.prefered_gender=""
        self.prefered_age=""
        self.paired_user=None
        self.RPS=None

    def is_going_to_new_state(self, event):
        return event.message.text == "new_state"

    def on_enter_new_state(self, event):
        id = event.source.user_id
        send_text_message(id, "enter new state")
    
    def is_going_to_user(self, event):
        return event.message.text == "user"

    # User State #####################
    def show_menu(self, event):
        if event.type == "follow":
            return True
        elif event.message.text == "@bot":
            return True
        else:
            return False

    def on_enter_user(self, event=None):
        send_button_message(self.line_id, "LineTalk", "開始與其他人聊天吧~", [
                            ("設定個人資訊", "設定個人資訊"), ("配對設定", "配對設定"), ("開始配對", "開始配對")])
    ##################################

    # Setting Introduction State #####
    def is_going_to_intro(self, event):
        text = event.message.text
        return text == "設定個人資訊"

    def on_enter_intro(self, event):
        id = event.source.user_id
        send_button_message(id, "設定個人資訊", "選擇要設定的項目", [
                            ("暱稱", "我要設定暱稱"), ("性別", "我要設定性別"), ("年齡", "我要設定年齡"), ("完成", "完成設定")])

    def set_intro(self, event):
        id = event.source.user_id
        if event.message.text == "完成設定":
            # TODO: Print out introduction
            return True
        else:
            return False
    ##################################

    # Setting Nickname State #########
    def is_going_to_intro_nickname(self, event):
        text = event.message.text
        return text == "我要設定暱稱"

    def on_enter_intro_nickname(self, event):
        id = event.source.user_id
        send_text_message(id, "請輸入暱稱")

    def set_intro_nickname(self, event):
        id = event.source.user_id
        text = event.message.text
        self.nickname = text
        send_text_message(id, "已儲存「" + text + "」為你的暱稱")
        return True
    ##################################

    # Setting Gender State #########
    def is_going_to_intro_gender(self, event):
        text = event.message.text
        return text == "我要設定性別"

    def on_enter_intro_gender(self, event):
        id = event.source.user_id
        send_button_message(id, "請選擇性別", "從下列選項選擇你的性別", [
                            ("男生", "男生"), ("女生", "女生"), ("其他", "其他")])

    def set_intro_gender(self, event):
        text = event.message.text
        id = event.source.user_id
        if text == "男生" or text == "女生" or text == "其他":
            self.gender = text
            send_text_message(id, "已儲存「" + text + "」為你的性別")
            return True
        else:
            send_text_message(id, "請重新選擇性別")
            return False
    ##################################

    # Setting Age State #########
    def is_going_to_intro_age(self, event):
        text = event.message.text
        return text == "我要設定年齡"

    def on_enter_intro_age(self, event):
        id = event.source.user_id
        send_text_message(id, "請輸入年齡")

    def set_intro_age(self, event):
        id = event.source.user_id
        text = event.message.text
        if text.isnumeric():
            self.age = int(text)
            send_text_message(id, "已儲存「" + text + "」為你的年齡")
            return True
        else:
            send_text_message(id, "請重新選擇年齡")
            return False
    ##################################

    # Setting Preference State #####
    def is_going_to_preference(self, event):
        text = event.message.text
        return text == "配對設定"

    def on_enter_preference(self, event):
        id = event.source.user_id
        send_button_message(id, "設定配對", "選擇希望配對的對象", [
                            ("性別", "我要設定性別"), ("年齡", "我要設定年齡"), ("完成", "完成設定")])

    def set_preference(self, event):
        id = event.source.user_id
        if event.message.text == "完成設定":
            # TODO: Print out preference
            return True
        else:
            return False
    ##################################

    # Prefered Age State #########
    def is_going_to_prefered_age(self, event):
        text = event.message.text
        return text == "我要設定年齡"

    def on_enter_prefered_age(self, event):
        id = event.source.user_id
        send_text_message(id, "請輸入年齡")

    def set_prefered_age(self, event):
        text = event.message.text
        id = event.source.user_id
        if text.isnumeric():
            self.prefered_age = int(text)
            send_text_message(id, "已儲存「" + text + "」為你希望配對到的年齡")
            return True
        else:
            send_text_message(id, "請重新選擇年齡")
            return False
    ##################################

    # Prefered Gender State #########
    def is_going_to_prefered_gender(self, event):
        text = event.message.text
        return text == "我要設定性別"

    def on_enter_prefered_gender(self, event):
        id = event.source.user_id
        send_button_message(id, "請選擇性別", "從下列選項選擇你希望配對到的性別", [
                            ("男生", "男生"), ("女生", "女生"), ("其他", "其他")])

    def set_prefered_gender(self, event):
        text = event.message.text
        id = event.source.user_id
        if text == "男生" or text == "女生" or text == "其他":
            self.prefered_gender = text
            send_text_message(id, "已儲存「" + text + "」為你希望配對到的性別")
            return True
        else:
            send_text_message(id, "請重新選擇性別")
            return False
    ##################################

    # Pairing State ##################
    def is_going_to_pairing(self, event):
        text = event.message.text
        return text == "開始配對"

    def on_enter_pairing(self, event):
        if not self.system.pair(self):
            id = event.source.user_id
            send_button_message(id, "正在幫你配對...", "請耐心等候", [("取消配對❌", "取消配對❌")])

    def cancel_pairing(self, event):
        text = event.message.text
        if text == "取消配對❌":
            self.system.cancel_pair(self)
            return True
        else:
            return False
    ##################################

    # Chating State ##################
    def call_bot(self, event):
        if event.message.text == "@bot":
            id = event.source.user_id
            send_button_message(id, "選項", "選擇你要的動作", [("我要猜拳🖐", "我要猜拳🖐"), ("幫我想話題💬", "幫我想話題💬"), ("我要離開🏃", "我要離開🏃")])
            return True
        else:
            return False

    def talking(self, event):
        text = event.message.text
        if text != "@bot" and text != "我要猜拳🖐" and text != "幫我想話題💬" and text != "我要離開🏃" and text != "拒絕猜拳⛔":
            send_text_message(self.paired_user.line_id, text)
            return True
        elif text == "幫我想話題💬":
            random_topic = random.sample(topic_list, 3)
            send_button_message(self.line_id, "選擇話題", "選擇一個傳送吧", [(x, x) for x in random_topic])
            return True
        else:
            return False
    
    def is_going_to_RPS(self, event):
        return event.message.text == "我要猜拳🖐"

    def on_enter_RPS(self, event):
        send_button_message(self.line_id, "開始猜拳", "選擇你要出什麼", [('剪刀✌', '剪刀✌'), ('石頭👊', '石頭👊'), ('布🖐', '布🖐'), ('取消猜拳❌', '取消猜拳❌')])

    def is_going_to_waiting_RPS(self, event):
        text = event.message.text
        if text == '剪刀✌' or text == '石頭👊' or text == '布🖐':
            if self.paired_user.RPS:
                self.RPS = text
            else:
                send_confirm_message(self.paired_user.line_id, "對方發起了猜拳", "對方發起了猜拳，你要接受嗎?", [('接受', '我要猜拳🖐'), ('拒絕', '拒絕猜拳⛔')])
                self.RPS = text
            return True
        else:
            return False
    
    def cancel_RPS(self, event):
        return event.message.text == '取消猜拳❌'

    def reject_RPS(self, event):
        if event.message.text == '拒絕猜拳⛔':
            send_text_message(self.paired_user.line_id, "對方拒絕了猜拳😭")
            self.paired_user.RPS = None
            self.paired_user.finish_RPS()
            return True
        else:
            return False

    def waiting_and_talking(self, event):
        text = event.message.text
        if text == "@bot":
            send_button_message(self.line_id, "選項", "選擇你要的動作", [("取消猜拳❌", "取消猜拳❌"), ("幫我想話題💬", "幫我想話題💬"), ("我要離開🏃", "我要離開🏃")])
            return True
        elif text == "取消猜拳❌":
            self.RPS = None
            self.finish_RPS()
            return False
        elif text == "幫我想話題💬":
            random_topic = random.sample(topic_list, 3)
            send_button_message(self.line_id, "選擇", "選擇一個傳送吧", [(x, x) for x in random_topic])
            return True
        elif text == "我要離開🏃":
            self.RPS = None
            return False
        else:
            send_text_message(self.paired_user.line_id, event.message.text)
            return True

    def on_enter_waiting_RPS(self, event):
        self.system.finished_RPS(self)

    def leaving(self, event):
        if event.message.text == "我要離開🏃":
            id = event.source.user_id
            self.system.leave(self)
            send_text_message(id, "你離開了聊天室👋")
            return True
        else:
            return False
    ##################################