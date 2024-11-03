def calculate_bmi_group(bmi: float | int) -> int:
    if bmi < 16:
        return 1
    if 16 <= bmi < 18.5:
        return 2
    if 18.5 <= bmi < 25:
        return 3
    if 25 <= bmi < 30:
        return 4
    if 30 <= bmi < 35:
        return 5
    if 35 <= bmi < 40:
        return 6
    return 7
