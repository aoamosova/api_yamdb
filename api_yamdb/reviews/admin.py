from django.contrib import admin

from .models import (Categories, Comments, Genres, Ratings, Reviews, Titles,
                     User)

admin.site.register(User)
admin.site.register(Titles)
admin.site.register(Categories)
admin.site.register(Genres)
admin.site.register(Reviews)
admin.site.register(Comments)
admin.site.register(Ratings)
