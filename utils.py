import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, actions, messages, TemplateSendMessage, MessageTemplateAction, ConfirmTemplate
from linebot.models.template import ButtonsTemplate


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)


def send_text_message(id, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.push_message(id, TextSendMessage(text=text))
    return "OK"


def send_image_url(id, img_url):
    return "OK"


def send_button_message(id, title, text, buttons):
    line_bot_api = LineBotApi(channel_access_token)
    actions = [MessageTemplateAction(label=x[0], text=x[1]) for x in buttons]
    line_bot_api.push_message(id, TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            title=title,
            text=text,
            actions=actions,
        )
    ))
    return "OK"

def send_confirm_message(id, title, text, buttons):
    line_bot_api = LineBotApi(channel_access_token)
    actions = [MessageTemplateAction(label=x[0], text=x[1]) for x in buttons]
    line_bot_api.push_message(id, TemplateSendMessage(
        alt_text='Buttons template',
        template=ConfirmTemplate(
            title=title,
            text=text,
            actions=actions,
        )
    ))
    return "OK"