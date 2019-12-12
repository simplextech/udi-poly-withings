

def seconds_to_minutes(seconds):
    minutes = round(float(seconds) / 60, 1)
    return minutes


def minutes_to_hours(minutes):
    hours = round(float(minutes) / 60, 1)
    return hours


def meters_to_feet(meters):
    ft = round((float(meters) / 1000) * 3.2808, 1)
    return ft


def meters_to_mile(meters):
    mi = round((float(meters) * 0.0006213712), 2)
    return mi


def json_to_normal(val):
    norm = round(val / 1000, 2)
    return norm


def kilogram_to_pound(kilogram):
    lb = round(float(kilogram) * 2.2046, 2)
    return lb


def kilogram_to_pound_weight(kilogram):
    lb = round(float(kilogram) * 2.2046 / 1000, 2)
    return lb


def kilogram_to_pound_mass(kilogram):
    lb = round(float(kilogram) * 2.2046 / 100, 2)
    return lb


def fahrenheit_to_celsius(fahrenheit):
    f = round((float(fahrenheit) - 32) * 5/9, 1)
    return f


def celsius_to_fahrenheit(celsius):
    c = round((float(celsius) * 9/5) + 32, 1)
    return c


def beats_per_minute(beats):
    bpm = float(beats) / 60
    return bpm

