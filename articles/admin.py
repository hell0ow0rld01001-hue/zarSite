from django.contrib import admin
from .models import Articles, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


class ArticlesAdmin(admin.ModelAdmin):
    inlines = [
        CommentInline
    ]
    list_display = [
        "title",
        "body",
        "author"
    ]


admin.site.register(Articles, ArticlesAdmin)
admin.site.register(Comment)
