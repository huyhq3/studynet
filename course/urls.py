from django.urls import path
from course import views

urlpatterns = [
    path('', views.get_courses),
    path('get_front_courses/', views.get_front_courses),
    path('get_categories/', views.get_categories),
    path('get_author_courses/<int:user_id>/', views.get_author_courses),
    path('create/', views.create_course),
    path('update/<slug:slug>/', views.update_course),
    path('<slug:slug>/', views.get_course),

    path('<slug:course_slug>/lessons/create/', views.create_lesson),
    path('<slug:course_slug>/<slug:lesson_slug>/update/', views.update_lesson),

    path('<slug:course_slug>/<slug:lesson_slug>/', views.add_comment),
    path('<slug:course_slug>/<slug:lesson_slug>/get-comments/', views.get_comments),
    path('<slug:course_slug>/<slug:lesson_slug>/get-quiz/', views.get_quiz),
]
