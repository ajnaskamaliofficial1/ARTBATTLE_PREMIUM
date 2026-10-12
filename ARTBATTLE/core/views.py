import hashlib

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import RegisterForm, ProfileForm, ArtworkForm
from .models import ArtistProfile, Battle, Artwork, Vote, Winner


def profile_for(user):
    profile, _ = ArtistProfile.objects.get_or_create(
        user=user,
        defaults={"display_name": user.username},
    )
    return profile


def home(request):
    active = (
        Battle.objects.filter(status__in=["open", "voting"])
        .order_by("voting_deadline")
        .first()
    )

    featured = (
        Artwork.objects.select_related("artist", "battle")
        .order_by("-votes", "-created_at")[:6]
    )

    leaders = ArtistProfile.objects.order_by("-rating", "-wins")[:5]

    return render(
        request,
        "core/home.html",
        {
            "active": active,
            "featured": featured,
            "leaders": leaders,
        },
    )


def battles(request):
    battle_list = Battle.objects.all().order_by("-start_at")

    return render(
        request,
        "core/battles.html",
        {"battles": battle_list},
    )


def battle_detail(request, pk):
    battle = get_object_or_404(Battle, pk=pk)

    artworks = (
        battle.artworks.select_related("artist")
        .order_by("-votes", "-created_at")
    )

    voted_ids = set()

    if request.user.is_authenticated:
        voted_ids = set(
            Vote.objects.filter(
                voter=request.user,
                artwork__battle=battle,
            ).values_list("artwork_id", flat=True)
        )

    return render(
        request,
        "core/battle_detail.html",
        {
            "battle": battle,
            "artworks": artworks,
            "voted_ids": voted_ids,
        },
    )


@login_required
def submit_artwork(request, pk):
    battle = get_object_or_404(Battle, pk=pk)
    now = timezone.now()

    # Accept submissions only while the battle is open
    # and the submission window is active.
    if (
        battle.status != "open"
        or not (battle.start_at <= now <= battle.submission_deadline)
    ):
        messages.error(
            request,
            "Submissions are closed for this battle.",
        )
        return redirect("battle_detail", pk=pk)

    artist = profile_for(request.user)

    # Multiple artworks per artist per battle are allowed.
    if request.method == "POST":
        form = ArtworkForm(request.POST, request.FILES)

        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.battle = battle
            artwork.artist = artist

            uploaded_image = form.cleaned_data["image"]

            # Calculate a hash to detect exact duplicate files
            # within this particular battle.
            original_position = uploaded_image.tell()
            image_hash = hashlib.sha256(
                uploaded_image.read()
            ).hexdigest()
            uploaded_image.seek(original_position)

            duplicate_exists = Artwork.objects.filter(
                battle=battle,
                image_hash=image_hash,
            ).exists()

            if duplicate_exists:
                form.add_error(
                    "image",
                    "This exact image has already been submitted "
                    "to this battle. Please upload a different image.",
                )
            else:
                artwork.image_hash = image_hash

                artwork.integrity_status = (
                    "AI declared"
                    if artwork.ai_declared
                    else "Basic duplicate check passed"
                )

                artwork.save()

                # Count unique battles entered by this artist.
                artist.battles_joined = (
                    Artwork.objects.filter(artist=artist)
                    .values("battle_id")
                    .distinct()
                    .count()
                )

                artist.save(update_fields=["battles_joined"])

                messages.success(
                    request,
                    "Your artwork has been submitted successfully!",
                )

                return redirect(
                    "artwork_detail",
                    pk=artwork.pk,
                )

    else:
        form = ArtworkForm()

    return render(
        request,
        "core/submit.html",
        {
            "battle": battle,
            "form": form,
        },
    )


def artwork_detail(request, pk):
    artwork = get_object_or_404(
        Artwork.objects.select_related("artist", "battle"),
        pk=pk,
    )

    voted = False

    if request.user.is_authenticated:
        voted = Vote.objects.filter(
            artwork=artwork,
            voter=request.user,
        ).exists()

    return render(
        request,
        "core/artwork_detail.html",
        {
            "art": artwork,
            "voted": voted,
        },
    )


@login_required
def vote(request, pk):
    if request.method != "POST":
        return redirect("artwork_detail", pk=pk)

    artwork = get_object_or_404(
        Artwork.objects.select_related("battle", "artist"),
        pk=pk,
    )

    if artwork.battle.status != "voting":
        messages.error(
            request,
            "Voting is not open for this battle.",
        )
        return redirect("battle_detail", pk=artwork.battle_id)

    if artwork.artist.user_id == request.user.id:
        messages.error(
            request,
            "You cannot vote for your own artwork.",
        )
        return redirect("artwork_detail", pk=pk)

    try:
        with transaction.atomic():
            Vote.objects.create(
                artwork=artwork,
                voter=request.user,
            )

            Artwork.objects.filter(pk=artwork.pk).update(
                votes=artwork.votes + 1
            )

        messages.success(request, "Your vote has been recorded.")

    except IntegrityError:
        messages.info(
            request,
            "You have already voted for this artwork.",
        )

    return redirect("artwork_detail", pk=pk)


def leaderboard(request):
    leaders = (
        ArtistProfile.objects.annotate(
            vote_total=Sum("artworks__votes")
        )
        .order_by("-rating", "-wins", "-vote_total")
    )

    return render(
        request,
        "core/leaderboard.html",
        {"leaders": leaders},
    )


def artists(request):
    artist_list = (
        ArtistProfile.objects.annotate(
            art_count=Count("artworks")
        )
        .order_by("-rating", "-wins")
    )

    return render(
        request,
        "core/artists.html",
        {"artists": artist_list},
    )


def artist_profile(request, username):
    user = get_object_or_404(User, username=username)
    artist = profile_for(user)

    artworks = (
        artist.artworks.select_related("battle")
        .order_by("-votes", "-created_at")
    )

    return render(
        request,
        "core/artist.html",
        {
            "artist": artist,
            "arts": artworks,
        },
    )


def winners(request):
    winner_list = (
        Winner.objects.select_related(
            "battle",
            "artwork",
            "artwork__artist",
        )
        .order_by("-awarded_at")
    )

    return render(
        request,
        "core/winners.html",
        {"wins": winner_list},
    )


def monthly(request):
    monthly_battles = (
        Battle.objects.filter(is_monthly=True)
        .order_by("-start_at")
    )

    return render(
        request,
        "core/monthly.html",
        {"battles": monthly_battles},
    )


@login_required
def edit_profile(request):
    artist = profile_for(request.user)

    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=artist,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")

            return redirect(
                "artist_profile",
                username=request.user.username,
            )
    else:
        form = ProfileForm(instance=artist)

    return render(
        request,
        "core/edit_profile.html",
        {"form": form},
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            ArtistProfile.objects.get_or_create(
                user=user,
                defaults={
                    "display_name": form.cleaned_data["display_name"],
                },
            )

            login(request, user)

            return redirect("home")
    else:
        form = RegisterForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )

        if user is not None:
            login(request, user)

            return redirect(
                request.GET.get("next") or "home"
            )

        messages.error(
            request,
            "Invalid username or password.",
        )

    return render(
        request,
        "registration/login.html",
    )


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def submit_select(request):
    now = timezone.now()

    # Show only battles that are currently accepting submissions.
    available_battles = Battle.objects.filter(
        status="open",
        start_at__lte=now,
        submission_deadline__gte=now,
    ).order_by("submission_deadline")

    return render(
        request,
        "core/submit_select.html",
        {"battles": available_battles},
    )