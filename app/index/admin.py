from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from userauth.models import User

from index.models import Index, Proposition, Publication

admin.site.register(Index)
admin.site.register(Publication)
admin.site.register(Proposition)

admin.site.enable_nav_sidebar = False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "username",
                    "password",
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            _("Profile"),
            {"fields": ("picture",)},
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_staff", "is_superuser", "user_permissions")},
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "last_name",
                    "first_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    list_display = (
        "icon",
        "username",
        "is_active",
        "is_staff",
        "is_superuser",
    )
    list_display_links = ("icon", "username")
    search_fields = ("username",)
    ordering = ("username",)

    readonly_fields = ("id", "picture_preview")

    def icon(self, obj):
        return (
            mark_safe(
                f'<img style="border-radius: 20%; object-fit: cover;" src="{obj.picture.url}" width=40 height=40 />'
            )
            if obj.picture
            else None
        )

    icon.short_description = "Picture"

    def picture_preview(self, obj):
        return (
            mark_safe(
                f'<img style="border-radius: 25%; object-fit: cover;" src="{obj.picture.url}" width=150 height=150 />'
            )
            if obj.picture
            else None
        )
