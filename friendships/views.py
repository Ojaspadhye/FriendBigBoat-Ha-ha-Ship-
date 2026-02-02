from friends_user.models import Friends_user
from .models import Friendship
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


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

    return Response({"message": "User Created! One of us! One of us!"}, status=201)


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
        return Response({"error": "Fuck not an option"}, status=400)

    try:
        fr = Friendship.objects.get(id=friendship_id, to_friend=request.user, status='PENDING')
    except Friendship.DoesNotExist:
        return Response({"error": "Friend request not found"}, status=404)

    if action == "ACCEPTED":
        fr.status = "ACCEPTED"
        fr.save()
        return Response({"message": f"You are now friends with {fr.from_friend.username}"}, status=200)

    elif action == "REJECT":
        fr.status = "REJECT"
        fr.save()
        return Response({"message": f"Friend request from {fr.from_friend.username} rejected"}, status=200)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_friends_accepted(request):
    user = request.user

    friends_accepted = Friendship.objects.filter(
        Q(from_friend=user) | Q(to_friend=user),
        status='ACCEPTED'
    )

    friend_accepted_data = [
        {
            "username": fr.friend2.username if fr.friend1 == user else fr.friend1.username,
            "pfp": (fr.friend2.pfp.url if fr.friend1 == user else fr.friend1.pfp.url),
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


