from friends_user.models import Friends_user
from .models import Friendship
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q


# Create your views here.

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sending_friends_request(request):
    to_friend = request.data.get("to_username")

    if not to_friend:
        return Response({"error": "I know you dont have Friends"}, status=400)
    
    if to_friend == request.user.username:
        return Response({"error": "You cannot be your own friend"}, status=400)

    try:
        to_user = Friends_user.objects.get(username=to_friend)
    except Friends_user.DoesNotExist:
        return Response({"error": "No User"}, status=404)
    
    if Friendship.objects.filter(from_friend=request.user, to_friend=to_user).exists():
        return Response({"error": "Chillout Alredy sent"}, status=400)
    
    if Friendship.objects.filter(from_friend=to_user, to_friend=request.user, status='ACCEPTED').exists():
        return Response({"error": "I also whish some of my friends meet me again like that time"}, status=400)

    Friendship.objects.create(from_friend=request.user, to_friend=to_user, status='PENDING')
    return Response({"message": f"Friend request sent to {to_user.username}"}, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_pending_request(request):
    user = request.user

    friends_pending = Friendship.objects.filter(to_friend=user, status='PENDING')

    pending_friend_requests = [
        {
            "from_friend": fr.from_friend.username,
            "sent_at": fr.from_date,
            "friendship_id": fr.id
        } for fr in friends_pending
    ]

    return Response({"pending_requests": pending_friend_requests}, status=200)


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

    else:
        fr.status = "BLOCKED"
        fr.save()
        return Response({"message": f"Friend request from {fr.from_friend.username} rejected"}, status=200)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_friends(request):
    user = request.user

    friends_accepted = Friendship.objects.filter(
        Q(from_friend=user) | Q(to_friend=user),
        status='ACCEPTED'
    )

    friend_accepted_data = [
        {
            "username": fr.to_friend.username if fr.from_friend == user else fr.from_friend.username,
            "pfp": (fr.to_friend.pfp.url if fr.from_friend == user else fr.from_friend.pfp.url) if fr.to_friend.pfp or fr.from_friend.pfp else None,
            "friendship_id": fr.id,
            "connected_since": fr.from_date
        } for fr in friends_accepted
    ]

    return Response({"friends": friend_accepted_data}, status=200)
