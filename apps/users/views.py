from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserRegistrationSerializer, UserUpdateSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet pour les utilisateurs"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Un utilisateur ne voit que son profil sauf si admin"""
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_serializer_class(self):
        """Sélectionne le sérialiseur approprié"""
        if self.action == 'register':
            return UserRegistrationSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        """Permissions personnalisées par action"""
        if self.action == 'register':
            return [permissions.AllowAny()]
        elif self.action in ['me', 'update_me']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Inscription d'un nouvel utilisateur"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            'message': 'Utilisateur créé avec succès',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Endpoint pour gérer son propre profil"""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            serializer = UserUpdateSerializer(
                request.user,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout (pour JWT token invalidation côté client)"""
        return Response({
            'message': 'Logout réussi. Supprimez le token JWT côté client.'
        })
