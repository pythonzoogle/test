from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from chat.models import ChatMessage,BotMsgToAll
from .serializers import UserMessagesSerializer,BroadcastMessageSerializer
from rest_framework.generics import (ListAPIView, RetrieveAPIView,
	UpdateAPIView,DestroyAPIView,CreateAPIView,RetrieveUpdateAPIView)
from rest_framework.filters import ( SearchFilter, OrderingFilter)
from rest_framework.permissions import (AllowAny,IsAuthenticated,
	IsAdminUser,IsAuthenticatedOrReadOnly)
#from .permissions import IsOwnerOrReadOnly,IsOwner
from rest_framework.pagination import (LimitOffsetPagination)
from .pagination import MessagesPageNumberPagination
from itertools import chain
from operator import attrgetter


#for testing chating with jwt authentication 
@login_required
def index_api(request):#add /?token=token to the url and then chat
    if not request.user.is_staff or not request.user.is_superuser:
        raise PermissionDenied   
    return render(request, "api-index/index.html")


#list messages of specific user
class UserMessagesListAPIView(ListAPIView):
	#permission_classes = [AllowAny]#default=AllowAny
	permission_classes = [IsAuthenticated]
	serializer_class = UserMessagesSerializer
	#you can use query params like this abc.com/?limit=8&offset=0 
	#means get 8 messages starting from the first message.
	#if no query params used then all messages will return.
	pagination_class = LimitOffsetPagination

	def get_queryset(self,*args,**kwargs):

		#user and bot messages sent to the specific user
		chat_msgs_qs = ChatMessage.objects.filter(user=self.request.user).order_by('timestamp')
		#bot messages sent to all existing users
		bot_msgs_qs = BotMsgToAll.objects.order_by('timestamp')
		#joining the two list querysets into one sorted list queryset
		#sorted by -timestamp cause reverse is True
		queryset_list = sorted(chain(chat_msgs_qs,bot_msgs_qs),key=attrgetter('timestamp'),reverse=True)
		
		return queryset_list

#list all messages
class MessagesListAPIView(ListAPIView):
	queryset = ChatMessage.objects.all()
	#permission_classes = [AllowAny]#default=AllowAny
	permission_classes = [IsAdminUser] #only admin can.
	serializer_class = UserMessagesSerializer
	filter_backends = [SearchFilter,OrderingFilter]
	search_fields = ['user__email','user__username','user__last_name','owner','timestamp']
	pagination_class = MessagesPageNumberPagination

#send broadcast message
class BroadcastMessageSendAPIView(CreateAPIView):
	serializer_class = BroadcastMessageSerializer
	permission_classes = [IsAdminUser]

	def perform_create(self, serializer):
		serializer.save(staff=self.request.user)	

