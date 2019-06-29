from fact.models import ActivityLevel, CalorieBurnt, CalorieIntake, MealDetail


def top_food(top=10):
    dist_food = {}
    calorie_intake = CalorieIntake.objects.all()
    for intake in calorie_intake:
        if intake.food is not None:
            if intake.food.name not in dist_food:
                dist_food[intake.food.name] = 0

            dist_food[intake.food.name] += intake.qty
        else:
            meals = MealDetail.objects.filter(meal=intake.meal.id)
            for meal in meals:
                if meal.food.name not in dist_food:
                    dist_food[meal.food.name] = 0

                dist_food[meal.food.name] += (intake.qty * meal.qty)

    list_food = []
    for key, value in dist_food.items():
        list_food.append((value, key))

    list_food.sort(reverse=True)
    return list_food[:top]


def top_user(date_start, date_end, top=5):
    calorie_food = CalorieIntake.objects.filter(created_at__gte=date_start, created_at__lte=date_end)
    calorie_activity = CalorieBurnt.objects.filter(created_at__gte=date_start, created_at__lte=date_end)
    dict_list_user_intake = {}
    dict_list_user_burnt = {}
    dict_user_tdee = {}
    dict_user = {}
    dict_username = {}

    for calorie in calorie_food:
        user_id = calorie.user.id
        day = calorie.created_at.day - 1

        if user_id not in dict_user_tdee:
            last_date_activity = ActivityLevel.objects.filter(user=user_id).latest("created_at")
            dict_user_tdee[user_id] = last_date_activity.tdee

        if user_id not in dict_list_user_intake:
            dict_list_user_intake[user_id] = [0] * 31  # 31 days

        if user_id not in dict_user:
            dict_user[user_id] = 0
            dict_user[user_id] = calorie.user.name

        if dict_user[user_id] == 1:
            continue

        if calorie.food is not None:
            dict_list_user_intake[user_id][day] += calorie.food.calorie * calorie.qty
        else:
            meals = MealDetail.objects.filter(meal=calorie.meal.id)
            for meal in meals:
                dict_list_user_intake[user_id][day] += meal.food.calorie * meal.qty * calorie.qty

        if dict_user_tdee[user_id] - 100 <= dict_list_user_intake[user_id][day] <= dict_user_tdee[user_id] + 100:
            dict_user[user_id] += 1

    for calorie in calorie_activity:
        user_id = calorie.user.id
        day = calorie.created_at.day - 1

        if user_id not in dict_user_tdee:
            last_date_activity = ActivityLevel.objects.filter(user=user_id).latest("created_at")
            dict_user_tdee[user_id] = last_date_activity.tdee

        if user_id not in dict_list_user_burnt:
            dict_list_user_burnt[user_id] = [0] * 31  # 31 days

        if user_id not in dict_user or dict_user[user_id] == 2:
            continue

        dict_list_user_burnt[user_id][day] += calorie.activity_label.met * calorie.user.weight * calorie.duration / 3600
        if dict_user_tdee[user_id] - 100 <= dict_list_user_burnt[user_id][day] <= dict_user_tdee[user_id] + 100:
            dict_user[user_id] += 1

    list_user = []
    for key, value in dict_user.items():
        list_user.append((value, dict_username[key]))

    list_user.sort(reverse=True)
    return list_user[:top]