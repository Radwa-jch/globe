!pip install requests geopy pandas
# Import libraries
import requests
import datetime
from geopy.geocoders import Nominatim

# User inputs
city = input("Enter city name: ")
activity = input("Enter your activity: ")
event_date_str = input("Enter planned event date (YYYY-MM-DD): ")
event_date = datetime.datetime.strptime(event_date_str, "%Y-%m-%d").date()

# Get city coordinates
geolocator = Nominatim(user_agent="weather_ai_app")
location = geolocator.geocode(city)
if location is None:
    print("City not found. Please check spelling and try again.")
    exit()

latitude = location.latitude
longitude = location.longitude

print(f"City: {city} -> Latitude: {latitude}, Longitude: {longitude}")

# Function to fetch weather safely
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


# Function to check if weather is suitable
def check_weather(temp, rain, wind, activity):
    activity = activity.lower()
    if activity in ["football", "soccer", "running", "cycling"]:
        return "suitable" if 15 <= temp <= 30 and rain < 1 and wind < 6 else "not suitable"
    elif activity in ["swimming", "picnic"]:
        return "suitable" if 20 <= temp <= 35 and rain < 2 else "not suitable"
    else:
        return "suitable" if 10 <= temp <= 35 and rain < 3 else "not suitable"

# Check main event date safely
times, temperatures, precipitations, winds = fetch_weather(event_date)

if not (times and temperatures and precipitations and winds):
    print("No forecast data available for this date/city.")
    print("Try a different date or city, or check alternative days below.\n")
    times = temperatures = precipitations = winds = None
else:
    forecast_time = times[0]
    temperature = temperatures[0]
    precipitation = precipitations[0]
    wind = winds[0]
    decision = check_weather(temperature, precipitation, wind, activity)

    print("===== Weather Activity Summary =====")
    print(f"Location: {city}")
    print(f"Event Date: {event_date}")
    print(f"Temperature: {temperature} °C")
    print(f"Precipitation: {precipitation} mm")
    print(f"Wind Speed: {wind} m/s")
    print("-----------------------------------")

    if decision == "suitable":
        print(f"The weather is suitable for {activity} on the planned date.")
    else:
        print(f"The weather is NOT suitable for {activity} on the planned date.")

# Suggest alternative days safely
alternative_found = False
for delta in range(1, 8):
    alt_date = event_date + datetime.timedelta(days=delta)
    times_alt, temps_alt, rain_alt, wind_alt = fetch_weather(alt_date)
    if times_alt and temps_alt and rain_alt and wind_alt:
        decision_alt = check_weather(temps_alt[0], rain_alt[0], wind_alt[0], activity)
        if decision_alt == "suitable":
            alternative_found = True
            print("\nSuggested Alternative Day:")
            print(f"Date: {alt_date}")
            print(f"Temperature: {temps_alt[0]} °C")
            print(f"Precipitation: {rain_alt[0]} mm")
            print(f"Wind Speed: {wind_alt[0]} m/s")
            break

if not alternative_found:
    print("\nNo suitable day found within 7 days. Consider an indoor activity.")
    alternative_activities = ["reading", "gym", "movie", "shopping"]
    print(f"Suggested indoor activity: {alternative_activities[0]}")
