from django.db import models

from core.enums import PendingItemStatus
from core.models.common import Identifiable, Representable, Storable, Traceable
from userauth.models import User


class Collection(Identifiable, Representable, Traceable, Storable):
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collections",
    )

    def __str__(self):
        return f"Collection {self.name} created by {self.creator}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name"],
                name="unique_collection_name",
            ),
        ]


class AbstractItem(Identifiable, Representable, Traceable, Storable):
    class Meta:
        abstract = True


class Item(AbstractItem):
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="items"
    )

    def __str__(self):
        return f"Item {self.name} of {self.collection}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "collection"],
                name="unique_item_collection_name",
            ),
        ]


class PendingItem(AbstractItem):
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="pending_items"
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pending_items",
    )
    status = models.TextField(
        choices=PendingItemStatus.choices,
        default=PendingItemStatus.PENDING,
    )

    def __str__(self):
        return f"Pending item {self.name} of {self.collection} from {self.creator}"


class Snap(Identifiable, Traceable, Storable):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="snaps")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="snaps")
    comment = models.CharField(max_length=255)
    dominant_colors = models.JSONField(null=True, blank=True)
    object_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Snap of {self.user} on {self.item}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "user"],
                name="unique_item_user",
            ),
        ]


class Like(Traceable):
    snap = models.ForeignKey(Snap, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    liked = models.BooleanField(default=True)

    def __str__(self):
        like = "Like" if self.liked else "Dislike"
        return f"{like} by {self.user} on {self.snap}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["snap", "user"],
                name="unique_like_user_snap",
            ),
        ]
