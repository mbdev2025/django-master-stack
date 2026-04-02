from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Organization(models.Model):
    """Modèle Organisation pour le multi-tenancy"""
    name = models.CharField(_('nom'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True, max_length=100)
    description = models.TextField(_('description'), blank=True)
    logo = models.ImageField(_('logo'), upload_to='organizations/logos/', blank=True, null=True)

    # Contact
    email = models.EmailField(_('email'), blank=True)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)
    website = models.URLField(_('site web'), blank=True)

    # Address
    address = models.TextField(_('adresse'), blank=True)
    city = models.CharField(_('ville'), max_length=100, blank=True)
    postal_code = models.CharField(_('code postal'), max_length=10, blank=True)
    country = models.CharField(_('pays'), max_length=100, blank=True)

    # Business
    industry = models.CharField(_('secteur'), max_length=100, blank=True)
    company_size = models.CharField(
        _('taille entreprise'),
        max_length=20,
        choices=[
            ('1-10', '1-10 employés'),
            ('11-50', '11-50 employés'),
            ('51-200', '51-200 employés'),
            ('201-500', '201-500 employés'),
            ('500+', '500+ employés'),
        ],
        blank=True
    )

    # Settings
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('organisation')
        verbose_name_plural = _('organisations')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def member_count(self):
        return self.members.count()

class Team(models.Model):
    """Modèle Team au sein d'une organisation"""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name=_('organisation')
    )
    name = models.CharField(_('nom'), max_length=200)
    description = models.TextField(_('description'), blank=True)

    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('équipe')
        verbose_name_plural = _('équipes')
        ordering = ['organization', 'name']

    def __str__(self):
        return f"{self.organization.name} - {self.name}"

class Member(models.Model):
    """Modèle Member pour les utilisateurs d'une organisation"""
    ROLE_CHOICES = [
        ('owner', 'Propriétaire'),
        ('admin', 'Administrateur'),
        ('member', 'Membre'),
        ('viewer', 'Visiteur'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name=_('utilisateur')
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        verbose_name=_('organisation')
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        related_name='members',
        verbose_name=_('équipe'),
        null=True,
        blank=True
    )
    role = models.CharField(_('rôle'), max_length=20, choices=ROLE_CHOICES, default='member')

    # Notifications & Settings
    job_title = models.CharField(_('poste'), max_length=100, blank=True)
    phone = models.CharField(_('téléphone'), max_length=20, blank=True)

    is_active = models.BooleanField(_('active'), default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('membre')
        verbose_name_plural = _('membres')
        unique_together = ['user', 'organization']
        ordering = ['organization', 'role', 'user']

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.organization.name} ({self.get_role_display()})"
