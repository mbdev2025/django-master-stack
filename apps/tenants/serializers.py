from rest_framework import serializers
from .models import Organization, Team, Member

class OrganizationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour Organisation"""
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'email', 'phone', 'website',
            'address', 'city', 'postal_code', 'country',
            'industry', 'company_size',
            'is_active', 'member_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_member_count(self, obj):
        return obj.member_count()

class TeamSerializer(serializers.ModelSerializer):
    """Sérialiseur pour Team"""
    member_count = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Team
        fields = [
            'id', 'organization', 'organization_name', 'name', 'description',
            'member_count', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_member_count(self, obj):
        return obj.members.count()

class MemberSerializer(serializers.ModelSerializer):
    """Sérialiseur pour Member"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True)

    class Meta:
        model = Member
        fields = [
            'id', 'user', 'user_email', 'user_full_name',
            'organization', 'organization_name',
            'team', 'team_name', 'role',
            'job_title', 'phone', 'is_active', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']

class CreateOrganizationSerializer(serializers.ModelSerializer):
    """Sérialiseur pour créer une organisation avec un owner"""
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True, max_length=150)
    last_name = serializers.CharField(write_only=True, max_length=150)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = Organization
        fields = [
            'name', 'slug', 'description',
            'email', 'first_name', 'last_name', 'password',
            'industry', 'company_size'
        ]

    def create(self, validated_data):
        # Créer l'utilisateur owner
        from apps.users.models import User
        user_data = {
            'email': validated_data.pop('email'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'password': validated_data.pop('password'),
            'role': 'admin'
        }
        user = User.objects.create_user(**user_data)

        # Créer l'organisation
        org = Organization.objects.create(**validated_data)

        # Créer le membership owner
        Member.objects.create(
            user=user,
            organization=org,
            role='owner',
            job_title='Owner'
        )

        return org
