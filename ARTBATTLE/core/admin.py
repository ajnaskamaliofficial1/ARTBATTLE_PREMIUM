from django.contrib import admin
from .models import ArtistProfile, Battle, Artwork, Vote, Winner
@admin.register(ArtistProfile)
class ArtistAdmin(admin.ModelAdmin):
    list_display=("display_name","rating","wins","top_three","battles_joined")
    search_fields=("display_name","user__username")
@admin.register(Battle)
class BattleAdmin(admin.ModelAdmin):
    list_display=("title","theme","status","start_at","submission_deadline","voting_deadline","is_monthly")
    list_filter=("status","is_monthly")
@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display=("title","artist","battle","votes","integrity_status","ai_declared")
    list_filter=("integrity_status","ai_declared")
@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display=("artwork","voter","created_at")
@admin.register(Winner)
class WinnerAdmin(admin.ModelAdmin):
    list_display=("battle","artwork","rank","awarded_at")
