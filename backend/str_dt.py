from datetime import datetime

def str_from_dt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def str_to_dt(s):
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

def hr_min_from_dt(dt):
    return dt.strftime("%H:%M")
