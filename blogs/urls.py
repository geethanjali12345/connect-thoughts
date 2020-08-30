
from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from .views import BlogsList,BlogDetail,AddBlog,UpdateBlog,DeleteBlog,user_profile,like_post,AddProfile,edit_user_profile,tagged,authorpostsview,post_by_category,signup,signout

urlpatterns = [
    path('',BlogsList, name='home'),
    path('blogs',BlogsList,name='blogs'),
    path('blog/<int:pk>',BlogDetail,name='blog-detail'),
    path('add/', login_required(AddBlog.as_view()), name="add-blog"),
    path('blog/<int:pk>/edit', UpdateBlog.as_view(), name='blog-update'),
    path('blog/<int:pk>/delete',DeleteBlog.as_view(),name='delete-blog'),
    path('tag/<slug:slug>/', tagged, name="tagged"),
    path('category/<slug:slug>/', post_by_category, name="category"),
    path('myblogs',authorpostsview,name='myblogs'),
    path('signup/',signup,name='signup'),
    path('like/',like_post,name='like_post'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('profile',user_profile,name='profile'),
    path('profile/add',AddProfile.as_view(),name='add-profile'),
    path('profile/edit',edit_user_profile,name='edit-profile'),
    path('logout/', signout, name='logout'),
]