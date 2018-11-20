import json
import time
from channels import Channel,Group
# from channels.sessions import channel_session
from channels.auth import channel_session_user_from_http, channel_session_user

from .models import ChatMessage

# Connected to chat.receive channel
# chat_send is chat.receive channel consumer
@channel_session_user
def chat_send(message):
    print("chat_send")
    owner = "user"
    user = message.user #dont forget to check if user exist in DB 
    msg = message.content['message']
    print(user.username,msg)     
    # Save to model
    msg_obj = ChatMessage.objects.create(
        user = user,
        message = msg,
        owner = owner
    )
    if(msg_obj):
        final_msg = {
            "user":msg_obj.user.username,
            "msg": msg_obj.message,
            "owner": msg_obj.owner,
            "timestamp":msg_obj.formatted_timestamp
        }
    else:
        final_msg = {
            "user":user.username,
            "msg": "sorry ,DB error",
            "owner": owner,    
        }    
    print("final_msg",final_msg)
    # Broadcast to listening socket(send user message to the user himself)
    message.reply_channel.send({"text": json.dumps(final_msg)})

    #bot listening logic
    payload = {
        'reply_channel': message.content['reply_channel'],
        'message': msg
    }
    Channel("bot.receive").send(payload)


# Connected to bot.receive channel
# bot_send is bot.receive channel consumer
# bot consumer 
@channel_session_user
def bot_send(message):
    print("bot_send")
    owner = "bot"
    user = message.user 
    msg = message.content['message']
    #bot logic
    msg = msg + "  ,bot reply"
    time.sleep(1)
    #then
    # Save to model
    msg_obj = ChatMessage.objects.create(
        user = user,
        message = msg,
        owner = owner
    )
    if(msg_obj):
        final_msg = {
            "user":msg_obj.user.username,
            "msg": msg_obj.message,
            "owner": msg_obj.owner,
            "timestamp":msg_obj.formatted_timestamp
        }
    else:
        final_msg = {
            "user":user.username,
            "msg": "sorry ,DB error",
            "owner": owner,    
        }  
    print("final_msg",final_msg)
    # Broadcast to listening socket(send bot reply message to the user)
    message.reply_channel.send({"text": json.dumps(final_msg)})





# Connected to websocket.connect
@channel_session_user_from_http
def ws_connect(message):
    print("ws_connect")
    # Accept connection
    message.reply_channel.send({"accept": True})
    #add each user to all-users group when they connect,
    #so that they can recieve any bot announce message. 
    Group("all-users").add(message.reply_channel)
    


# Connected to websocket.receive
def ws_receive(message):
    payload = json.loads(message['text'])
    payload['reply_channel'] = message.content['reply_channel']
    print("ws_receive", message['text'],payload)
    # Stick the message onto the processing queue
    Channel("chat.receive").send(payload)

# Connected to websocket.disconnect
def ws_disconnect(message):
    print("ws_disconnect")
    #remove each user from all-users group when they disconnect.
    Group("all-users").discard(message.reply_channel)