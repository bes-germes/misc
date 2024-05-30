import csv

list = [
    "type_aiming",
    "polusph",
    "treb_nav_vrem",
    "treb_skritn",
    "treb_nav_zadn",
    "predp_nav_zadn",
    "real_v_pr",
    "real_v_man",
    "real_v_per",
    "real_tr_pr",
    "real_tr_man",
    "real_tr_per",
    "real_top_pr",
    "real_top_man",
    "real_top_per"
]

def check_condition(conditions):
    for condition in conditions:
        if condition:
            return False
    return True

def undefined(dict):
    return dict["type_aiming"] == "радиолокационный" and dict["treb_skritn"] == "1"

if __name__ == '__main__':

    rows = []

    with open('C:/Users/olezh/labsPy/misc/lab1/input.csv', newline='', encoding="UTF-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row[0][:-1])

    dict = dict(zip(list, rows))

    condition_straight_aiming = [
        (dict["real_v_pr"] == "0" or dict["real_tr_pr"] == "0" or dict["real_top_pr"] == "0"),
    ]

    condition_maneuver = [
        (dict["real_v_man"] == "0" or dict["real_tr_man"] == "0" or dict["real_top_man"] == "0"),
    ]

    condition_interception = [
        (dict["type_aiming"] == "тепловой" or dict["treb_skritn"] == "1") and (dict["polusph"] == "передняя"),
        (dict["real_v_per"] == "0" or dict["real_tr_per"] == "1") and (dict["real_top_per"] == "0"),
        (dict["predp_nav_zadn"] == "1" and (check_condition(condition_maneuver) or check_condition(condition_straight_aiming))
         and (dict["polusph"] == "передняя")),
        (dict["treb_nav_zadn"] == "1" and dict["polusph"] == "передняя"),
    ]

    is_straight_aiming = check_condition(condition_straight_aiming)
    is_maneuver = check_condition(condition_maneuver)
    is_interception = check_condition(condition_interception)

    choosed_method = None

    if undefined(dict) or (not is_straight_aiming and not is_straight_aiming and not is_interception):
        choosed_method = "НИКАКОЙ"
    elif is_interception:
        choosed_method = "Метод ПЕРЕХВАТА"
    elif is_straight_aiming:
        choosed_method = "Метод ПРЯМОГО НАВЕДЕНИЯ"
    elif is_maneuver:
        choosed_method = "Метод МАНЁВРА"

    print("Выбранный метод наведения: " + choosed_method)





