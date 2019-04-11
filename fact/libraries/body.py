from datetime import datetime


def calculate_bmi(user):
    return user.weight / (user.height ** 2)


def calculate_bmr(user):
    bmr = -1
    age = datetime.now().year - user.birth_year

    if age <= 3:
        bmr = 60.9 * user.weight - 54 if user.gender.id == 1 else 61.0 * user.weight - 51

    elif age <= 10:
        bmr = 22.7 * user.weight + 495 if user.gender.id == 1 else 22.5 * user.weight + 499

    elif age <= 15:
        bmr = 17.5 * user.weight + 651 if user.gender.id == 1 else 12.2 * user.weight + 746

    elif age <= 30:
        bmr = 15.3 * user.weight + 679 if user.gender.id == 1 else 14.7 * user.weight + 496

    elif age <= 60:
        bmr = 11.6 * user.weight + 879 if user.gender.id == 1 else 8.7 * user.weight + 829

    else:
        bmr = 13.5 * user.weight + 487 if user.gender.id == 1 else 10.5 * user.weight + 596

    return bmr


def calculate_activity_factor(user, level):
    activity_factor = -1

    if level == "low":
        activity_factor = 1.56 if user.gender.id == 1 else 1.55

    elif level == "medium":
        activity_factor = 1.76 if user.gender.id == 1 else 1.70

    elif level == "high":
        activity_factor = 2.10 if user.gender.id == 1 else 2.00

    return activity_factor
