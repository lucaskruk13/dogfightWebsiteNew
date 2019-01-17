"""DogfightWebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from feed import views as feed_views
from accounts import views as account_views
from django.contrib.auth import views as auth_views
from feed import views as course_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Feed Urls
    path('', feed_views.FeedView.as_view(), name='feed'),
    path('course/<int:pk>/', feed_views.CourseView.as_view(), name='course'),
    path('dogfightSignup/<int:dogfight_pk>/<int:user_pk>/', feed_views.dogfight_signup, name='dogfight_signup'),
    path('cancelDogfightSignup/<int:dogfight_pk>/<int:user_pk>/', feed_views.cancel_dogfight_signup, name='cancel_dogfight_signup'),

    # Profile
    path('profile/<int:user_pk>/', account_views.ProfileView.as_view(template_name='accounts/profile.html'), name='profile'),
    path('profile/<int:user_pk>/edit/', account_views.ProfileUpdateView.as_view(template_name='accounts/edit_profile.html'), name='edit_profile'),

    # Admin Urls
    path('admin/', admin.site.urls),

    # Auth Urls
    path('signup/', account_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='accounts/auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='accounts/auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/auth/password_reset_complete.html'), name='password_reset_complete'),


    path('reset/', auth_views.PasswordResetView.as_view(
        template_name="accounts/auth/password_reset.html",
        email_template_name='accounts/auth/password_reset_email.html',
        subject_template_name='accounts/auth/password_reset_subject.txt'
    ),
    name='password_reset'),

    # Settings
    path('settings/account/', account_views.ProfileUpdateView.as_view(), name='my_account'),
    path('settings/password/', auth_views.PasswordChangeView.as_view(template_name='accounts/auth/password_change.html'), name='password_change'),
    path('settings/password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/auth/password_change_done.html'),name='password_change_done'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)