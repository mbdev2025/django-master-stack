from django.contrib import admin
from .models import Organization, Team, Member

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'industry', 'company_size', 'is_active', 'created_at']
    list_filter = ['is_active', 'industry', 'company_size', 'created_at']
    search_fields = ['name', 'email', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'member_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['name', 'organization__name']

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Membres'

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'team', 'job_title', 'joined_at']
    list_filter = ['role', 'organization', 'team', 'joined_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'organization__name']
