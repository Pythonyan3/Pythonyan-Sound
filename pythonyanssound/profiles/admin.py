from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfileCreationForm, ProfileChangeForm
from .models import Profile


class AdminProfile(UserAdmin):
    """
    Profile model settings for correct displaying data in django admin
    list_display -- list of displaying fields in Profile model main page table
    list_filter -- list of displaying fields in filter panel (django admin)

    fieldsets -- tuple of groups of model fields displaying on Model info page
    add_fieldsets -- tuple of groups of model fields displaying on Model Add page
    search_fields -- tuple of fields that used in search
    ordering -- list of fields that used in ordering
    """
    add_form = ProfileCreationForm
    form = ProfileChangeForm
    model = Profile

    list_display = ('username', 'email', 'is_staff', 'is_confirmed', 'is_active',)
    list_filter = ('is_staff', 'is_confirmed', 'is_active',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'photo', 'biography')}),
        ('Permissions', {'fields': ('is_staff', 'is_confirmed', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'photo', 'biography', 'password1', 'password2', 'is_staff',
                       'is_confirmed', 'is_active')}
         ),
    )
    search_fields = ('username', 'email',)
    ordering = ('username',)

    filter_horizontal = ()


admin.site.register(Profile, AdminProfile)
