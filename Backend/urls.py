"""Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
# from django.contrib import admin
from django.urls import path
from SmartMove import views

urlpatterns = [
    #    path('admin/', admin.site.urls),
    path('auth/register', views.register),
    path('auth/login', views.login),
    path('user/logout', views.logout),
    path('user/profile', views.profile),
    path('trainee/profile', views.trainee_profile),
    path('trainee/profile/weight', views.trainee_weight),
    path('trainee/profile/height', views.trainee_height),
    path('trainee/coaches', views.trainee_coaches),
    path('trainee/coach', views.trainee_coach),
    path('trainee/exercises', views.assigned_exercises),
    path('trainee/report', views.exercises_report),
    path('coach/profile', views.coach_profile),
    path('coach/trainee/exercises', views.coach_assigned_exercises),
    path('coach/trainees/<str:traineeId>/exercise/<int:exerciseId>', views.coach_assign_exercise),
    path('coach/exercises', views.coach_exercises),
]
