from rest_framework.decorators import api_view, permission_classes

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response


@api_view(['GET'])

@permission_classes([IsAuthenticated])

def me(request):

    user = request.user

    role = user.profile.role if hasattr(user, 'profile') else None

    return Response({

    'id': user.id,

    'username': user.username,

    'email': user.email,

    'role': role,

    })