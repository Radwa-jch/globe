# Install required packages
!pip install requests geopy pandas
# Import libraries
import requests
import datetime
from geopy.geocoders import Nominatim
import calendar

# -----------------------
# User inputs
# -----------------------
city = input("Enter city name: ").strip()
activity = input("Enter your activity: ").strip()

# Handle month input safely
month_input = input("Enter month (e.g., March): ").strip().lower()
month_dict = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12
}
month = month_dict.get(month_input)
if month is None:
    print("Invalid month name.")
    exit()

# Handle week input safely
week_input = input("Enter week number (1, 2, 3, 4): ").strip()
if not week_input.isdigit() or not (1 <= int(week_input) <= 4):
    print("Invalid week selection.")
    exit()
week = int(week_input)

# Default year
year = datetime.datetime.now().year

# Calculate number of days in month
_, last_day_of_month = calendar.monthrange(year, month)

# Calculate start and end days of the week
start_day = 1 + (week - 1) * 7
end_day = min(start_day + 6, last_day_of_month)

start_date = datetime.date(year, month, start_day)
end_date = datetime.date(year, month, end_day)

print(f"Checking weather for {city}, {month_input.title()} week {week} ({start_date} to {end_date})")

# -----------------------
# Get city coordinates
# -----------------------
geolocator = Nominatim(user_agent="weather_ai_app")
location = geolocator.geocode(city)
if location is None:
    print("City not found. Please check spelling and try again.")
    exit()

latitude = location.latitude
longitude = location.longitude
print(f"City: {city} -> Latitude: {latitude}, Longitude: {longitude}")

# -----------------------
# Function to fetch weather safely for a date
# -----------------------
def fetch_weather(date):
    date_str = date.strftime("%Y%m%d")
    url = f"https://power.larc.nasa.gov/api/temporal/hourly/point?parameters=T2M,PRECTOTCORR,WS2M&community=RE&longitude={longitude}&latitude={latitude}&start={date_str}&end={date_str}&format=JSON"
    response = requests.get(url)
    data = response.json()
    times = list(data.get("properties", {}).get("parameter", {}).get("T2M", {}).keys())
    temperatures = list(data.get("properties", {}).get("parameter", {}).get("T2M", {}).values())
    precipitations = list(data.get("properties", {}).get("parameter", {}).get("PRECTOTCORR", {}).values())
    winds = list(data.get("properties", {}).get("parameter", {}).get("WS2M", {}).values())
    return times, temperatures, precipitations, winds

# -----------------------
# Function to check if weather is suitable
# -----------------------
def check_weather(temp, rain, wind, activity):
    activity = activity.lower()
    if activity in ["football", "soccer", "running", "cycling"]:
        return "suitable" if 15 <= temp <= 30 and rain < 1 and wind < 6 else "not suitable"
    elif activity in ["swimming", "picnic"]:
        return "suitable" if 20 <= temp <= 35 and rain < 2 else "not suitable"
    else:
        return "suitable" if 10 <= temp <= 35 and rain < 3 else "not suitable"

# -----------------------
# Loop over each day in the week and find best day
# -----------------------
best_day = None
best_decision = "not suitable"
current_day = start_date
while current_day <= end_date:
    times, temps, rain, wind = fetch_weather(current_day)
    if times and temps and rain and wind:
        decision = check_weather(temps[0], rain[0], wind[0], activity)
        if decision == "suitable":
            best_day = current_day
            best_decision = decision
            best_temp = temps[0]
            best_rain = rain[0]
            best_wind = wind[0]
            break  # pick first suitable day
    current_day += datetime.timedelta(days=1)

# -----------------------
# Output results
# -----------------------
if best_day:
    print("===== Suggested Best Day for Activity =====")
    print(f"Date: {best_day}")
    print(f"Temperature: {best_temp} °C")
    print(f"Precipitation: {best_rain} mm")
    print(f"Wind Speed: {best_wind} m/s")
    print(f"The weather is suitable for {activity}!")
else:
    print("No suitable day found in this week. Consider an indoor activity.")
    indoor_activities = ["reading", "gym", "movie", "shopping"]
    print(f"Suggested indoor activity: {indoor_activities[0]}")
