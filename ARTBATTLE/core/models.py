import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class ArtistProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="artist"
    )
    display_name = models.CharField(max_length=80)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True
    )
    country = models.CharField(max_length=60, blank=True)
    website = models.URLField(blank=True)

    rating = models.PositiveIntegerField(default=0)
    wins = models.PositiveIntegerField(default=0)
    top_three = models.PositiveIntegerField(default=0)
    battles_joined = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.display_name or self.user.username


class Battle(models.Model):

    STATUS = [
        ("draft", "Draft"),
        ("open", "Open"),
        ("voting", "Voting"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=120)
    theme = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    start_at = models.DateTimeField()
    submission_deadline = models.DateTimeField()
    voting_deadline = models.DateTimeField()

    prize_text = models.CharField(
        max_length=160,
        default="Sponsor-funded prize"
    )
    prize_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default="draft"
    )

    is_monthly = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_at"]

    @property
    def is_active(self):
        now = timezone.now()

        return (
            self.status in ("open", "voting")
            and self.start_at <= now <= self.voting_deadline
        )

    @property
    def artwork_count(self):
        return self.artworks.count()

    def __str__(self):
        return self.title


class Artwork(models.Model):

    battle = models.ForeignKey(
        Battle,
        on_delete=models.CASCADE,
        related_name="artworks"
    )

    artist = models.ForeignKey(
        ArtistProfile,
        on_delete=models.CASCADE,
        related_name="artworks"
    )

    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="artworks/")

    medium = models.CharField(max_length=80, blank=True)
    ai_declared = models.BooleanField(default=False)

    image_hash = models.CharField(
        max_length=64,
        editable=False
    )

    created_at = models.DateTimeField(auto_now_add=True)

    votes = models.PositiveIntegerField(default=0)

    integrity_status = models.CharField(
        max_length=40,
        default="Pending review"
    )

    class Meta:
        ordering = ["-votes", "-created_at"]

    def save(self, *args, **kwargs):

        if self.image and hasattr(self.image, "read"):
            try:
                position = self.image.tell()
            except (OSError, ValueError):
                position = None

            image_content = self.image.read()

            self.image_hash = hashlib.sha256(
                image_content
            ).hexdigest()

            if position is not None:
                self.image.seek(position)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Vote(models.Model):

    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE,
        related_name="vote_records"
    )

    voter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="votes"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["artwork", "voter"],
                name="one_vote_per_user"
            )
        ]

    def __str__(self):
        return f"{self.voter.username} → {self.artwork.title}"


class Winner(models.Model):

    battle = models.OneToOneField(
        Battle,
        on_delete=models.CASCADE,
        related_name="winner"
    )

    artwork = models.ForeignKey(
        Artwork,
        on_delete=models.CASCADE
    )

    rank = models.PositiveIntegerField(default=1)

    awarded_at = models.DateTimeField(auto_now_add=True)

    prize_note = models.CharField(
        max_length=200,
        blank=True
    )

    def __str__(self):
        return f"{self.battle} — {self.artwork.artist}"