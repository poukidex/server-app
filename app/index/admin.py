from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from index.models import Approbation, Index, Proposition, Publication
from userauth.models import Token, User

admin.site.register(Index)
admin.site.register(Publication)
admin.site.register(Proposition)
admin.site.register(Approbation)

admin.site.enable_nav_sidebar = False

admin.site.register(Token)


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
                )
            },
        ),
        (
            _("Information"),
            {"fields": ("first_name", "last_name", "object_name", "picture_preview")},
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
                f'<img style="border-radius: 20%; object-fit: cover;" src="{obj.presigned_url}" width=40 height=40 />'
            )
            if obj.object_name
            else None
        )

    icon.short_description = "Picture"

    def picture_preview(self, obj):
        return (
            mark_safe(
                f'<img style="border-radius: 25%; object-fit: cover;" src="{obj.presigned_url}" width=150 height=150 />'
            )
            if obj.object_name
            else None
        )

    picture_preview.short_description = "Preview"
