from django.contrib import admin
from .models import Posts,Comment,Category
# Register your models here.
class PostsAdmin(admin.ModelAdmin):
	lists_display=['title','slug','user','content','tags','publish','updated_at','likes']
	prepopulated_fields={'slug':('title',)} 

class CategoryAdmin(admin.ModelAdmin):
	lists_display=['title']
	ordering = ['-id']
class CommentsAdmin(admin.ModelAdmin):
	lists_display=['post','user','time','comm']

admin.site.register(Posts,PostsAdmin)
admin.site.register(Comment,CommentsAdmin)
admin.site.register(Category,CategoryAdmin)