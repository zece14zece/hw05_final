from django.contrib import admin
from django.urls import include, path
from posts import views
from django.conf import settings
from django.conf.urls.static import static

posts_patterns = ([
    path('', views.index, name="index"),
    path('group/<slug:slug>/', views.group_posts, name='group_posts'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/comment', views.add_comment, name='add_comment'),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name="profile_unfollow"
    ),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit')
], 'posts')

urlpatterns = [
    path('', include(posts_patterns)),
    path('', include('posts.urls', namespace='post')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

# handler404 = 'core.views.page_not_found'
# handler403 = 'core.views.csrf_failure'
