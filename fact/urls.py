from django.urls import path
from . import views

urlpatterns = [
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("user", views.user, name="user"),

    path("check", views.check, name="check"),
    path("migrate", views.migrate_api, name="migrate_api"),
    path("compare", views.compare_api, name="compare_api"),
    path("calorie-burnt", views.calorie_burnt_api, name="calorie_burnt_api"),
    path("calorie-intake/food", views.calorie_burnt_food_api, name="calorie_burnt_food_api"),
    path("calorie-intake/meal", views.calorie_burnt_meal_api, name="calorie_burnt_meal_api"),
    path("self-train", views.self_train_api, name="self_train_api"),
    path("activity_level/new", views.activity_level_new_api, name="activity_level_new_api"),
    path("activity_level/review", views.activity_level_review_api, name="activity_level_review_api"),
]