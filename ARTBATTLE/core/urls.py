from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("battles/", views.battles, name="battles"),
    path("battle/<int:pk>/", views.battle_detail, name="battle_detail"),
    path("battle/<int:pk>/submit/", views.submit_artwork, name="submit_artwork"),
    path("artwork/<int:pk>/", views.artwork_detail, name="artwork_detail"),
    path("artwork/<int:pk>/vote/", views.vote, name="vote"),
    path("leaderboard/", views.leaderboard, name="leaderboard"),
    path("artists/", views.artists, name="artists"),
    path("artist/<str:username>/", views.artist_profile, name="artist_profile"),
    path("winners/", views.winners, name="winners"),
    path("monthly/", views.monthly, name="monthly"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("submit/", views.submit_select, name="submit_select"),
]
