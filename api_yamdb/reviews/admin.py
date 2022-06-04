from django.contrib import admin

from .models import Categories, Genres, Titles, User

admin.site.register(User)
admin.site.register(Titles)
admin.site.register(Categories)
admin.site.register(Genres)