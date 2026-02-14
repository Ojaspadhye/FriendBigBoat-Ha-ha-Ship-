from friends_user.models import Friends_user
from .models import Friendship, Messages
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
import datetime
import json
import redis

'''
1. sending request
2. get pending request
3. response to friend request
4. get all friend
5. balancing the request
'''

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sending_friends_request(request):
    to_friend = request.data.get("to_username")
    from_friend = request.user

    if not to_friend:
        return Response({"error": "I know you dont have Friends"}, status=400)
    
    if to_friend == from_friend.username:
        return Response({"error": "You cannot be your own friend"}, status=400)

    try:
        to_user = Friends_user.objects.get(username=to_friend)
    except Friends_user.DoesNotExist:
        return Response({"error": "No User"}, status=404)
    
    friend1, friend2 = (from_friend, to_user) if from_friend.id < to_user.id else (to_user, from_friend)

    if Friendship.objects.filter(friend1=friend1, friend2=friend2):
        return Response({"error": "Friendship Exists"}, status=400)

    Friendship.objects.create(
        friend1=friend1,
        friend2=friend2,
        sender=from_friend,
        status="PENDING"
    )

    return Response({"message": "Friendship Created US"}, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_pending_request_to_me(request):
    user = request.user

    friends_pending = Friendship.objects.filter( status='PENDING').exclude(sender=user)

    pending_friend_requests_to_me = [
        {
            "from_friend": fr.sender.username,
            "sent_at": fr.from_date,
            "friendship_id": fr.id
        } for fr in friends_pending
    ]

    return Response({"pending_requests": pending_friend_requests_to_me}, status=200)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def respond_friend_request(request):
    friendship_id = request.data.get("friendship_id")
    action = request.data.get("action")

    if not friendship_id or not action:
        return Response({"error": "friendship id and action not mentioned"}, status=400)

    if action not in ["ACCEPTED", "REJECT"]:
        return Response({"error": "Invalid action"}, status=400)

    try:
        fr = Friendship.objects.get(id=friendship_id, status='PENDING')
    except Friendship.DoesNotExist:
        return Response({"error": "Friend request not found"}, status=404)

    if request.user != fr.friend1 and request.user != fr.friend2:
        return Response({"error": "You cannot respond to this request"}, status=403)
    fr.status = action
    fr.save()

    sender = fr.friend1 if fr.friend1 != request.user else fr.friend2

    if action == "ACCEPTED":
        return Response({"message": f"You are now friends with {sender.username}"}, status=200)
    else:
        return Response({"message": f"Friend request from {sender.username} rejected"}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_friends_accepted(request):
    user = request.user

    friends_accepted = Friendship.objects.filter(
        Q(friend1=user) | Q(friend2=user),
        status='ACCEPTED'
    )

    friend_accepted_data = [
        {
            "friend_name": fr.friend2.username if fr.friend1 == user else fr.friend1.username,
            "friendship_id": fr.id,
            "connected_since": fr.from_date,
            "sender": fr.sender.username
        } for fr in friends_accepted
    ]

    return Response({"friends": friend_accepted_data}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_friend_waiting(request):
    user = request.user

    friends_pending = Friendship.objects.filter(sender=user, status="PENDING")

    friends_pending_sent_data = [
        {
            "username": fr.friend2.username if fr.friend1 == user else fr.friend1.username,
            "sent_at": fr.from_date,
            "friendship_id": fr.id
        } for fr in friends_pending
    ]

    return Response({"friends_pending_you_sent": friends_pending_sent_data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_messages_sender_reciver(request):
    user = request.user
    friend = request.data.get("friend_id")

    from_date = request.data.get("from_date")
    to_date = request.data.get("to_date")

    try:
        friend = Friends_user.objects.get(id=friend)
    except Friends_user.DoesNotExist:
        return Response({"error": "Friend not found"}, status=404)

    friend1, friend2 = (user, friend) if user.id < friend.id else (friend, user)
    
    try:
        channel_id = Friendship.object.filter(friend1=friend1, friend2=friend2)
    except Friendship.DoesNotExist:
        return Response({"error": "You have no chats setup"}, status=404)
    
    from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.datetime.strptime(to_date, "%Y-%m-%d")

    messages_filtered = Messages.objects.filter(
        channel=channel_id,
        received_at__range=(from_date, to_date)
    )

    messages_data = [
        {
            "channel_id": m.channel,
            "sender_username": m.sender,
            "reciver_username": m.receiver,
            "message": m.content
        }for m in messages_filtered
    ]
    return Response({"message_data": messages_data})


redis_client = redis.Redis(host="redis-13769.c245.us-east-1-3.ec2.cloud.redislabs.com", port=13769, db=0)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    user = request.user
    receiver_id = request.data.get("reciever")
    content = request.data.get("content")

    if not receiver_id or not content:
        return Response({"error": "No proper content"}, status=400)
    
    try:
        receiver_id = int(receiver_id)
        receiver = Friends_user.objects.get(id=receiver_id)
    except (ValueError, TypeError, Friends_user.DoesNotExist):
        return Response({"error": "No receiver found"}, status=404)

    # DEBUG: Check friendship exists in DB
    friendships = Friendship.objects.filter(
        Q(friend1=user, friend2=receiver) | Q(friend1=receiver, friend2=user)
    )
    print(friendships)  # <-- Add this temporarily to see what is in DB

    # Check for accepted friendship
    channel = friendships.filter(status='ACCEPTED').first()
    if not channel:
        return Response({"error": "No chat exists / not friends"}, status=403)

    message = {
        "sender": user.id,
        "receiver": receiver.id,
        "content": content,
        "timestamp": timezone.now().isoformat()
    }

    redis_key = f"chat:{channel.id}"
    redis_client.rpush(redis_key, json.dumps(message))

    return Response({"status": "sent", "channel": channel.id}, status=201)
