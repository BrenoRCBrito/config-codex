from datetime import date
from typing import Any

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.text import slugify


class GameQuerySet(models.QuerySet["Game"]):
    """Custom QuerySet for the simplified Game model."""

    def by_platform(self, platform: str) -> "GameQuerySet":
        """Filter games by platform."""
        return self.filter(platforms__contains=[platform])

    def by_genre(self, genre: str) -> "GameQuerySet":
        """Filter games by genre."""
        return self.filter(genres__contains=[genre])

    def by_engine(self, engine: str) -> "GameQuerySet":
        """Filter games by engine."""
        return self.filter(engine__icontains=engine)

    def by_series(self, series: str) -> "GameQuerySet":
        """Filter games by series."""
        return self.filter(series__icontains=series)

    def released_in_year(self, year: int) -> "GameQuerySet":
        """Filter games released in a specific year."""
        return self.filter(release_date__year=year)

    def search(self, query: str) -> "GameQuerySet":
        """Search games by name, developer, or publisher."""
        return self.filter(
            models.Q(name__icontains=query)
            | models.Q(developer__icontains=query)
            | models.Q(publisher__icontains=query)
        )


class GameManager(models.Manager["Game"]):
    """Custom manager for Game model."""

    def get_queryset(self) -> GameQuerySet:
        return GameQuerySet(self.model, using=self._db)

    def by_platform(self, platform: str) -> GameQuerySet:
        return self.get_queryset().by_platform(platform)

    def by_genre(self, genre: str) -> GameQuerySet:
        return self.get_queryset().by_genre(genre)

    def by_engine(self, engine: str) -> GameQuerySet:
        return self.get_queryset().by_engine(engine)

    def by_series(self, series: str) -> GameQuerySet:
        return self.get_queryset().by_series(series)

    def search(self, query: str) -> GameQuerySet:
        return self.get_queryset().search(query)


class Game(models.Model):
    """
    A simplified video game model for configuration categorization.

    This model contains core descriptive and technical attributes of a game,
    stripped of marketing, sales, and other commercial data.
    """

    class AgeRating(models.TextChoices):
        """ESRB age rating classifications."""

        EC = "EC", "Early Childhood"
        E = "E", "Everyone"
        E10 = "E10+", "Everyone 10+"
        T = "T", "Teen"
        M = "M", "Mature 17+"
        AO = "AO", "Adults Only 18+"
        RP = "RP", "Rating Pending"

    id = models.BigIntegerField(primary_key=True, editable=False, db_index=True)
    name = models.CharField(
        max_length=200, unique=True, db_index=True, help_text="Official game title"
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        db_index=True,
        help_text="URL-friendly version of the game name",
    )

    developer = models.CharField(
        max_length=100, db_index=True, help_text="Game developer/studio"
    )
    publisher = models.CharField(
        max_length=100, db_index=True, help_text="Game publisher"
    )
    release_date = models.DateField(db_index=True, help_text="Official release date")

    engine = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Game engine (e.g., Unreal Engine 5, Unity, Frostbite)",
    )
    series = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Game series or franchise (e.g., Call of Duty, Assassin's Creed)",
    )

    genres = ArrayField(
        models.CharField(max_length=50),
        size=10,
        default=list,
        blank=True,
        help_text="Game genres (e.g., Action, RPG, Strategy)",
    )
    platforms = ArrayField(
        models.CharField(max_length=50),
        size=20,
        default=list,
        blank=True,
        help_text="Supported platforms (e.g., PC, PlayStation, Xbox)",
    )
    tags = ArrayField(
        models.CharField(max_length=30),
        size=20,
        default=list,
        blank=True,
        help_text="Game tags for additional categorization",
    )

    age_rating = models.CharField(
        max_length=10,
        choices=AgeRating.choices,
        blank=True,
        help_text="ESRB age rating",
    )

    minimum_requirements = models.JSONField(
        default=dict, blank=True, help_text="Minimum system requirements"
    )
    recommended_requirements = models.JSONField(
        default=dict, blank=True, help_text="Recommended system requirements"
    )

    steam_id = models.CharField(
        max_length=20, blank=True, unique=True, null=True, help_text="Steam store ID"
    )
    igdb_id = models.CharField(
        max_length=20, blank=True, unique=True, null=True, help_text="IGDB database ID"
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    objects = GameManager()

    class Meta:
        db_table = "games"
        ordering = ["-release_date", "name"]
        indexes = [
            models.Index(fields=["developer", "publisher"]),
            models.Index(fields=["engine"]),
            models.Index(fields=["series"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.release_date.year if self.release_date else 'TBA'})"

    def __repr__(self) -> str:
        return f"Game(id={self.id}, name='{self.name}')"

    @property
    def is_released(self) -> bool:
        """Check if the game has been released."""
        return self.release_date is not None and self.release_date <= date.today()

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to ensure slug is generated and model is clean."""
        if not self.slug:
            self.slug = slugify(self.name)
        self.full_clean()
        super().save(*args, **kwargs)
