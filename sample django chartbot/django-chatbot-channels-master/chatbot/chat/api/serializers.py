from chat.models import ChatMessage ,BotMsgToAll
from django.contrib.auth import get_user_model
from rest_framework.serializers  import (ModelSerializer, 
HyperlinkedIdentityField, SerializerMethodField,
HyperlinkedRelatedField,ValidationError,EmailField,CharField,DateTimeField)


User = get_user_model()

class UserDetailSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ['username','email','first_name','last_name']

class UserMessagesSerializer(ModelSerializer):
	
	user = UserDetailSerializer(read_only=True)
	formated_timestamp = SerializerMethodField()

	class Meta:
		model = ChatMessage
		fields = ['user','message','owner','timestamp','formated_timestamp']
	
	def get_formated_timestamp(self,obj):
		return obj.formatted_timestamp

class BroadcastMessageSerializer(ModelSerializer):
	class Meta:
		model = BotMsgToAll
		fields = ['message']		