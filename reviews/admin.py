

from django.contrib import admin

from .models import Paper, Review

class ReviewAdmin(admin.ModelAdmin):
    model = Review
    raw_id_fields = ('paper',)
    search_fields = ('paper__name',)
    list_display = ('paper', 'rating', 'user_name', 'comment', 'pub_date')
    list_filter = ['pub_date', 'user_name']



admin.site.register(Paper)
admin.site.register(Review, ReviewAdmin)