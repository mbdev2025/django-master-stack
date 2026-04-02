from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Organization, Team, Member
from .serializers import (
    OrganizationSerializer, TeamSerializer, MemberSerializer,
    CreateOrganizationSerializer
)

class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet pour les organisations"""
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'industry', 'company_size']
    search_fields = ['name', 'description', 'email']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

    def get_queryset(self):
        """Un utilisateur voit uniquement ses organisations"""
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Organization.objects.all()
        return Organization.objects.filter(members__user=user)

    def get_serializer_class(self):
        if self.action == 'create_org':
            return CreateOrganizationSerializer
        return OrganizationSerializer

    def get_permissions(self):
        if self.action == 'create_org':
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def create_org(self, request):
        """Créer une organisation avec un owner"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        org = serializer.save()

        return Response({
            'message': 'Organisation créée avec succès',
            'organization': OrganizationSerializer(org).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def teams(self, request, pk=None):
        """Récupérer les équipes de l'organisation"""
        org = self.get_object()
        teams = org.teams.filter(is_active=True)
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Récupérer les membres de l'organisation"""
        org = self.get_object()
        members = org.members.filter(is_active=True).select_related('user')
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)

class TeamViewSet(viewsets.ModelViewSet):
    """ViewSet pour les équipes"""
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Un utilisateur voit uniquement les équipes de ses organisations"""
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Team.objects.all()
        return Team.objects.filter(organization__members__user=user)

class MemberViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les membres (lecture seule)"""
    serializer_class = MemberSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['organization', 'role', 'team']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

    def get_queryset(self):
        """Un utilisateur voit uniquement les membres de ses organisations"""
        user = self.request.user
        if user.is_staff or user.role == 'admin':
            return Member.objects.all()
        return Member.objects.filter(organization__members__user=user)
