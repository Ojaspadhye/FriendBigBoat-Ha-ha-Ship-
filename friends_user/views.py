from friends_user.models import Friends_user
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated



# Create your views here.

@api_view(["GET"])
def home_views(request):
    pass

@api_view(["POST"])
def signup_views(request):
    username = request.data.get("username")
    password = request.data.get("password")
    emailid = request.data.get("emailid")
    phone_no = request.data.get("phone_no")
    pfp = request.data.get("pfp")
    info = request.data.get("info")

    if not username or not password or not emailid or not phone_no:
        return Response({"error": "no username or imp thing provided"}, status=400)
    
    if Friends_user.objects.filter(username=username).exists():
        return Response({"error": "username usedup"}, status=400)
    
    if Friends_user.objects.filter(emailid=emailid).exists():
        return Response({"error": "email taken"}, status=400)
    
    if Friends_user.objects.filter(phone_no=phone_no).exists():
        return Response({"error": "phone taken"}, status=400)
    
    new_user = Friends_user(
        username=username,
        emailid=emailid,
        phone_no=phone_no,
        pfp=pfp,
        info=info,
    )

    new_user.set_password(password)
    new_user.save()

    refresh = RefreshToken.for_user(new_user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    
    return Response({
        "message": "User created",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "emailid": new_user.emailid
        }
    }, status=201)



@api_view(["POST"])
def login_views(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "username and password nor given"}, status=400)

    try:
        user = Friends_user.objects.get(username=username)
    except Friends_user.DoesNotExist:
        return Response({"error": "username or password not proper"}, status=400)

    if not user.check_password(password):
        return Response({"error": "Invalid username or password"}, status=400)
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    return Response({
        "message": "Fuck Yes! One of us! One of us! One of us!",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "emailid": user.emailid
        }
    }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_views(request):
    user = request.user
    return Response({
        "message": "To The Fucking Dashboard We go!",
        "user": {
            "id": user.id,
            "username": user.username,
            "emailid": user.emailid
        }
    }, status=200)
    