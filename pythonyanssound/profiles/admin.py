from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import ProfileCreationForm, ProfileChangeForm
from .models import Profile, SongLike


class SongLikeInline(admin.TabularInline):
    model = SongLike
    extra = 1


class AdminProfile(UserAdmin):
    """
    Profile model settings for correct displaying data in django admin.


    list_display - model fields displaying on main page table
    list_filter - model fields displaying on filter panel

    fieldsets - model fields displaying on record info page
    add_fieldsets - model fields displaying on record add page
    search_fields - model fields that used in search
    ordering - model fields which are used in ordering
    """
    add_form = ProfileCreationForm
    form = ProfileChangeForm
    model = Profile

    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'is_active', 'is_artist', 'is_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_artist', 'is_verified')

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password', 'photo', 'biography', )}),
        ("Many to many relations", {'fields': ('liked_playlists', 'followings',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_artist', 'is_verified', 'is_active', )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'photo', 'biography', 'password1', 'password2', 'is_staff', 'is_superuser',
                       'is_active', 'is_artist', 'is_verified')}
         ),
    )
    search_fields = ('username', 'email',)
    ordering = ('username',)

    filter_horizontal = ('liked_songs', 'liked_playlists', 'followings')
    inlines = (SongLikeInline,)


admin.site.register(Profile, AdminProfile)
