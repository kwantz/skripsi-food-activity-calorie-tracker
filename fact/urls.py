from django.urls import path
from . import views

urlpatterns = [
    # path("user", views.user, name="user"),

    path("check", views.check, name="check"),
    path("migrate", views.migrate_api, name="migrate_api"),
    path("compare", views.compare_api, name="compare_api"),

    path("calorie-burnt", views.calorie_burnt_api, name="calorie_burnt_api"),
    path("calorie-burnt/<int:activity_id>", views.calorie_burnt_detail_api, name="calorie_burnt_detail_api"),

    path("calorie-intake/food", views.calorie_intake_food_api, name="calorie_burnt_food_api"),
    path("calorie-intake/meal", views.calorie_intake_meal_api, name="calorie_burnt_meal_api"),
    path("calorie-intake/<int:food_id>", views.calorie_intake_detail_api, name="calorie_intake_detail_api"),

    path("self-train", views.self_train_api, name="self_train_api"),
    
    path("activity_level/new", views.activity_level_new_api, name="activity_level_new_api"),
    path("activity_level/review", views.activity_level_review_api, name="activity_level_review_api"),

    # Frontend
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),

    path("dashboard", views.dashboard_api, name="dashboard_api"),
    path("dashboard/new-users", views.new_user_api, name="new_user_api"),

    path("food", views.food_api, name="food_api"),
    path("food/<int:food_id>", views.food_detail_api, name="food_detail_api"),

    path("food-category", views.food_category_api, name="food_category_api"),
    path("food-category/all", views.all_food_category_api, name="all_food_category_api"),

    path("activity", views.activity_api, name="activity_api"),
    path("activity/<int:activity_id>", views.activity_detail_api, name="activity_detail_api"),

    path("images/<image>", views.testing_my_api, name="testing_my_api"),
    path("upload", views.upload_api, name="upload_api"),
    path("article", views.article_api, name="article_api"),

    path("quote", views.quote_api, name="quote_api"),
    path("quote/<int:quote_id>", views.quote_detail_api, name="quote_detail_api"),

    path("user", views.user_api, name="user_api"),
    path("user/<int:user_id>", views.user_detail_api, name="user_detail_api")
]