from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    FollowEvent,
    JoinEvent,
    LeaveEvent,
    MessageEvent,
    TextMessage,
    TextSendMessage,
    UnfollowEvent,
)

from bot.models import Channel

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.LINE_CHANNEL_SECRET)


@csrf_exempt
def callback(request):

    if request.method != "POST":
        return HttpResponseBadRequest()

    signature = request.META["HTTP_X_LINE_SIGNATURE"]
    body = request.body.decode("utf-8")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return HttpResponseForbidden()
    except LineBotApiError:
        return HttpResponseBadRequest()

    return HttpResponse()


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    profile = line_bot_api.get_profile(event.source.user_id)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(
            text=f"Hi {profile.display_name}, 收到您的訊息: {event.message.text}"
        ),
    )


@handler.add(FollowEvent)
def handle_follow(event):
    profile = line_bot_api.get_profile(event.source.user_id)

    Channel.objects.get_or_create(
        channel_id=event.source.user_id,
        defaults={
            "channel_type": event.source.type,
            "channel_name": profile.display_name,
        },
    )


@handler.add(UnfollowEvent)
def handle_unfollow(event):

    Channel.objects.filter(
        channel_id=event.source.user_id,
    ).delete()


@handler.add(JoinEvent)
def handle_join(event):
    group_profile = line_bot_api.get_group_summary(event.source.group_id)

    Channel.objects.get_or_create(
        channel_id=event.source.group_id,
        defaults={
            "channel_type": event.source.type,
            "channel_name": group_profile.group_name,
        },
    )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"大家好，我是小幫手"),
    )


@handler.add(LeaveEvent)
def handle_leave(event):

    Channel.objects.filter(
        channel_id=event.source.group_id,
    ).delete()
