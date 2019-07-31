from django.urls import path
from . import temp
from . import views

urlpatterns = [
    # General API
    path("check", views.api_check, name="api_check"),
    path("login", views.api_login, name="api_login"),
    path("register", views.api_register, name="api_register"),
    path("forgot-password", views.api_forgot_password, name="api_forgot_password"),
    path("reset-password/<forgot_password>", views.api_reset_password, name="api_reset_password"),
    path("confirm-email/<confirm_email>", views.api_confirm_email, name="api_confirm_email"),

    path("image/upload", views.api_upload, name="api_upload"),
    path("image/<image>", views.api_image, name="api_image"),

    path("migrate", views.api_migrate, name="api_migrate"),


    # API for Admin Web
    path("dashboard", views.api_dashboard, name="api_dashboard"),
    path("dashboard/new-users", views.api_new_user, name="api_new_user"),

    path("food", views.api_food, name="api_food"),
    path("food/<int:food_id>", views.api_food_detail, name="api_food_detail"),

    path("food-category", views.api_food_category, name="api_food_category"),
    path("food-category/<int:food_category_id>", views.api_food_category_detail, name="api_food_category_detail"),

    path("activity", views.api_activity, name="api_activity"),
    path("activity/<int:activity_id>", views.api_activity_detail, name="api_activity_detail"),

    path("quote", views.api_quote, name="api_quote"),
    path("quote/<int:quote_id>", views.api_quote_detail, name="api_quote_detail"),

    path("article", views.api_article, name="api_article"),
    path("article/<int:article_id>", views.api_article_detail, name="api_article_detail"),

    path("user", views.api_user, name="api_user"),
    path("user/<int:user_id>", views.api_user_detail, name="api_user_detail"),

    path("comparison", views.api_comparison, name="api_comparison"),
    path("comparison/upload", views.api_comparison_upload, name="api_comparison_upload"),


    # API for Member Web
    path("member/user", views.api_member_user_detail, name="api_member_user_detail"),
    path("member/diary", views.api_member_diary, name="api_member_diary"),
    path("member/newsfeed", views.api_member_newsfeed, name="api_member_newsfeed"),
    path("member/activity", views.api_member_activity, name="api_member_activity"),
    path("member/recent", views.api_member_recent, name="api_member_recent"),
    path("member/evaluation", views.api_member_evaluation, name="api_member_evaluation"),

    path("member/article", views.api_member_article, name="api_member_article"),
    path("member/article/<int:article_id>", views.api_member_article_detail, name="api_member_article_detail"),

    path("member/activity-label", views.api_member_activity_label, name="api_member_activity_label"),

    path("member/activity-level", views.api_member_activity_level, name="api_member_activity_level"),
    path("member/activity-level/review", views.api_member_activity_level_review, name="api_member_activity_level_review"),

    path("member/food", views.api_member_food, name="api_member_food"),
    path("member/meal", views.api_member_meal, name="api_member_meal"),
    path("member/meal/<int:meal_id>", views.api_member_meal_detail, name="api_member_meal_detail"),

    path("member/burnt", views.api_member_burnt, name="api_member_burnt"),

    path("member/intake", views.api_member_intake, name="api_member_intake"),
    path("member/intake/food", views.api_member_intake_food, name="api_member_intake_food"),
    path("member/intake/meal", views.api_member_intake_meal, name="api_member_intake_meal"),

    path("member/history/intake", views.api_member_history_intake, name="api_member_history_intake"),
    path("member/history/burnt", views.api_member_history_burnt, name="api_member_history_burnt"),

    # path("user", temp.user, name="user"),

    # path("check", temp.check, name="check"),
    # path("migrate", temp.migrate_api, name="migrate_api"),
    # path("compare", temp.compare_api, name="compare_api"),
    #
    # path("calorie-burnt", temp.calorie_burnt_api, name="calorie_burnt_api"),
    # path("calorie-burnt/<int:activity_id>", temp.calorie_burnt_detail_api, name="calorie_burnt_detail_api"),
    #
    # path("calorie-intake/food", temp.calorie_intake_food_api, name="calorie_burnt_food_api"),
    # path("calorie-intake/meal", temp.calorie_intake_meal_api, name="calorie_burnt_meal_api"),
    # path("calorie-intake/<int:food_id>", temp.calorie_intake_detail_api, name="calorie_intake_detail_api"),
    #
    # path("self-train", temp.self_train_api, name="self_train_api"),
    #
    # path("activity_level/new", temp.activity_level_new_api, name="activity_level_new_api"),
    # path("activity_level/review", temp.activity_level_review_api, name="activity_level_review_api"),

    # Frontend

    # path("images/<image>", temp.testing_my_api, name="testing_my_api"),
    # path("upload", temp.upload_api, name="upload_api"),
    # path("article", temp.article_api, name="article_api"),

]