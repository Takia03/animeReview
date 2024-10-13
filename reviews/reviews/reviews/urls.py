from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from animereviews import views  # Import views from your app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('<str:user_name>/home/', views.home, name='home'),  # Home page with user_name
    path('<str:user_name>/favorites/', views.favorites, name='favorites'),
    path('profile/<str:user_name>/', views.profile, name='profile'),
    path('suggestions/<str:user_name>/', views.suggestions, name='suggestions'),
    path('movie/<int:movie_id>/<str:user_name>/', views.movie_detail, name='movie_detail'),
    
    # Add this to handle the root URL
    path('', views.login, name='root_login'),  # Redirect root to login page
]

# Serve static files (only need to include once)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files in development (if needed)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
