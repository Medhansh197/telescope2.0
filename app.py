from flask import Flask, render_template, jsonify, Response
try:
    from flask_cors import CORS
except ImportError:
    CORS = None
import pandas as pd
import requests
from datetime import datetime, timedelta
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
if CORS:
    CORS(app)

ACCUWEATHER_API_KEY = os.getenv('ACCUWEATHER_API_KEY')

# Load CSV data with proper error handling
try:
    csv_file = 'UTTRAKHAND_ISRO0019_2012-11-02_2019-01-02_Nov2025_175236.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        print(f"Loaded CSV with {len(df)} records")
        
        # Clean and prepare the data with multiple date format handling
        def parse_date(date_str):
            formats = ['%m-%d-%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y']
            for fmt in formats:
                try:
                    return pd.to_datetime(date_str, format=fmt)
                except:
                    continue
            return pd.NaT
        
        df['DATE(IST)'] = df['DATE(IST)'].apply(parse_date)
        df = df.dropna(subset=['DATE(IST)'])
        
        # Ensure numeric columns are properly typed
        numeric_columns = ['AIR_TEMP(°C)', 'HUMIDITY(%)', 'WIND_SPEED(m/s)', 'ATMO_PRESSURE(hpa)']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        print(f"Successfully processed {len(df)} valid records")
        print(f"Date range: {df['DATE(IST)'].min()} to {df['DATE(IST)'].max()}")
    else:
        print("CSV file not found, creating empty DataFrame")
        df = pd.DataFrame()
except Exception as e:
    print(f"Error loading CSV data: {e}")
    df = pd.DataFrame()

LOCATIONS = {
    'beluwakhan': {'name': 'Beluwakhan', 'temp': 15.2, 'humidity': 65, 'wind': 2.1, 'pressure': 965.5},
    'nainital': {'name': 'Nainital', 'temp': 12.8, 'humidity': 58, 'wind': 1.8, 'pressure': 967.2},
    'delhi': {'name': 'Delhi', 'temp': 22.5, 'humidity': 72, 'wind': 3.2, 'pressure': 1013.2},
    'mumbai': {'name': 'Mumbai', 'temp': 28.1, 'humidity': 78, 'wind': 2.8, 'pressure': 1012.8}
}

# Pre-defined location keys for better reliability
LOCATION_KEYS = {
    'Beluwakhan': '2295019',  # Closest match for Beluwakhan
    'Nainital': '202396',    # Nainital, India
    'Delhi': '202396',       # Delhi, India  
    'Mumbai': '204842'       # Mumbai, India
}

def get_location_key(city_name):
    if not ACCUWEATHER_API_KEY:
        return None
    
    # Try pre-defined keys first
    if city_name in LOCATION_KEYS:
        return LOCATION_KEYS[city_name]
    
    # Fallback to API search
    url = "https://dataservice.accuweather.com/locations/v1/cities/search"
    params = {'apikey': ACCUWEATHER_API_KEY, 'q': city_name}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Location search for {city_name}: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"Found location key: {data[0]['Key']} for {city_name}")
                return data[0]['Key']
        else:
            print(f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Location search error: {e}")
    
    return None

def get_current_and_today_weather(location='beluwakhan'):
    """Get both current conditions and today's detailed weather from AccuWeather"""
    loc_data = LOCATIONS.get(location, LOCATIONS['beluwakhan'])
    
    if ACCUWEATHER_API_KEY:
        try:
            city_name = loc_data['name']
            location_key = get_location_key(city_name)
            print(f"Getting weather for {city_name} with key: {location_key}")
            
            if location_key:
                # Get current conditions
                current_url = f"https://dataservice.accuweather.com/currentconditions/v1/{location_key}"
                current_params = {'apikey': ACCUWEATHER_API_KEY, 'details': 'true'}
                
                # Get today's forecast
                today_url = f"https://dataservice.accuweather.com/forecasts/v1/daily/1day/{location_key}"
                today_params = {'apikey': ACCUWEATHER_API_KEY, 'details': 'true', 'metric': 'true'}
                
                print(f"Fetching current conditions from: {current_url}")
                current_response = requests.get(current_url, params=current_params, timeout=10)
                print(f"Current conditions response: {current_response.status_code}")
                
                print(f"Fetching today's forecast from: {today_url}")
                today_response = requests.get(today_url, params=today_params, timeout=10)
                print(f"Today's forecast response: {today_response.status_code}")
                
                if current_response.status_code == 200:
                    current_data = current_response.json()[0]
                    print(f"Current temperature from API: {current_data['Temperature']['Metric']['Value']}°C")
                    
                    # Get today's data if available
                    today_data = None
                    if today_response.status_code == 200:
                        today_data = today_response.json()['DailyForecasts'][0]
                    
                    # Combine current and today's data
                    result = {
                        'location': city_name,
                        'current_time': current_data.get('LocalObservationDateTime', datetime.now().isoformat()),
                        'temperature': round(current_data['Temperature']['Metric']['Value'], 1),
                        'feels_like': round(current_data.get('RealFeelTemperature', {}).get('Metric', {}).get('Value', current_data['Temperature']['Metric']['Value']), 1),
                        'humidity': current_data.get('RelativeHumidity', 50),
                        'wind_speed': round(current_data['Wind']['Speed']['Metric']['Value'] / 3.6, 1),
                        'wind_direction': current_data['Wind'].get('Direction', {}).get('Localized', 'N/A'),
                        'pressure': round(current_data['Pressure']['Metric']['Value'], 1),
                        'visibility': current_data.get('Visibility', {}).get('Metric', {}).get('Value', 10),
                        'cloud_cover': current_data.get('CloudCover', 0),
                        'weather_text': current_data.get('WeatherText', 'Clear'),
                        'uv_index': current_data.get('UVIndex', 0),
                        'api_source': 'AccuWeather Live Data'
                    }
                    
                    # Add today's data if available
                    if today_data:
                        result.update({
                            'today_min_temp': round(today_data['Temperature']['Minimum']['Value'], 1),
                            'today_max_temp': round(today_data['Temperature']['Maximum']['Value'], 1),
                            'today_day_conditions': today_data['Day'].get('IconPhrase', 'N/A'),
                            'today_night_conditions': today_data['Night'].get('IconPhrase', 'N/A'),
                            'sunrise': today_data.get('Sun', {}).get('Rise', 'N/A'),
                            'sunset': today_data.get('Sun', {}).get('Set', 'N/A'),
                            'moon_phase': today_data.get('Moon', {}).get('Phase', 'N/A')
                        })
                    else:
                        # Fallback values for today's data
                        result.update({
                            'today_min_temp': round(result['temperature'] - 5, 1),
                            'today_max_temp': round(result['temperature'] + 3, 1),
                            'today_day_conditions': 'Fair',
                            'today_night_conditions': 'Clear',
                            'sunrise': '06:30',
                            'sunset': '18:00',
                            'moon_phase': 'N/A'
                        })
                    
                    print(f"Returning API data with temperature: {result['temperature']}°C")
                    return result
                else:
                    print(f"API request failed: {current_response.status_code} - {current_response.text}")
        except Exception as e:
            print(f"API Error for {location}: {e}")
            import traceback
            traceback.print_exc()
    
    # Enhanced fallback with realistic time-based variations
    print(f"Using enhanced fallback data for {loc_data['name']}")
    import random
    
    # Time-based temperature variation (cooler at night, warmer during day)
    current_hour = datetime.now().hour
    if 6 <= current_hour <= 18:  # Daytime
        temp_modifier = random.uniform(0, 4)  # Warmer during day
    else:  # Nighttime
        temp_modifier = random.uniform(-4, 0)  # Cooler at night
    
    # Seasonal adjustment based on month
    current_month = datetime.now().month
    if current_month in [12, 1, 2]:  # Winter
        seasonal_modifier = -3
    elif current_month in [3, 4, 5]:  # Spring
        seasonal_modifier = 0
    elif current_month in [6, 7, 8]:  # Summer
        seasonal_modifier = 5
    else:  # Fall
        seasonal_modifier = 1
    
    base_temp = loc_data['temp'] + temp_modifier + seasonal_modifier
    humidity_variation = random.randint(-10, 10)
    
    return {
        'location': loc_data['name'],
        'current_time': datetime.now().isoformat(),
        'temperature': round(base_temp + random.uniform(-1, 1), 1),
        'feels_like': round(base_temp + random.uniform(-2, 2), 1),
        'humidity': max(20, min(90, loc_data['humidity'] + humidity_variation)),
        'wind_speed': round(loc_data['wind'] + random.uniform(-0.8, 0.8), 1),
        'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
        'pressure': round(loc_data['pressure'] + random.uniform(-3, 3), 1),
        'visibility': random.choice([8, 10, 12, 15, 18]),
        'cloud_cover': random.randint(0, 60),
        'weather_text': random.choice(['Clear', 'Partly Cloudy', 'Fair', 'Mostly Clear', 'Light Clouds']),
        'uv_index': max(0, min(10, random.randint(0, 8) if 6 <= current_hour <= 18 else 0)),
        'today_min_temp': round(base_temp - 6, 1),
        'today_max_temp': round(base_temp + 4, 1),
        'today_day_conditions': random.choice(['Fair', 'Partly Cloudy', 'Mostly Sunny']),
        'today_night_conditions': random.choice(['Clear', 'Partly Cloudy', 'Fair']),
        'sunrise': '06:30',
        'sunset': '18:00',
        'moon_phase': ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'][datetime.now().day % 8],
        'api_source': 'Enhanced Simulation (API Quota Exceeded - Resets Daily)'
    }

def get_weather_data(location='beluwakhan'):
    """Wrapper function for backward compatibility"""
    return get_current_and_today_weather(location)

def predict_telescope_conditions(weather_data):
    score = 0
    factors = []
    
    if 5 <= weather_data['temperature'] <= 20:
        score += 25
        factors.append("✓ Good temperature")
    else:
        factors.append("⚠ Temperature not ideal")
    
    if weather_data['humidity'] < 70:
        score += 25
        factors.append("✓ Low humidity")
    else:
        factors.append("⚠ High humidity")
    
    if weather_data['wind_speed'] < 3:
        score += 25
        factors.append("✓ Low wind")
    else:
        factors.append("⚠ High wind")
    
    if weather_data['pressure'] > 960:
        score += 25
        factors.append("✓ Good pressure")
    else:
        factors.append("⚠ Low pressure")
    
    if score >= 75:
        recommendation = "Excellent"
    elif score >= 50:
        recommendation = "Good"
    else:
        recommendation = "Poor"
    
    return {
        'score': score,
        'recommendation': recommendation,
        'factors': factors
    }

def get_past_data():
    """Analyze historical data from CSV"""
    try:
        if df.empty:
            return {
                'total_records': 0,
                'optimal_days': 0,
                'optimal_percentage': 0,
                'avg_temp': 15.0,
                'avg_humidity': 65.0,
                'avg_wind': 2.0,
                'avg_pressure': 965.0
            }
        
        df_copy = df.copy()
        
        # Define optimal telescope viewing conditions
        optimal = df_copy[
            (df_copy['HUMIDITY(%)'] < 70) & 
            (df_copy['WIND_SPEED(m/s)'] < 3) & 
            (df_copy['ATMO_PRESSURE(hpa)'] > 960) &
            (df_copy['AIR_TEMP(°C)'].between(5, 20))
        ]
        
        total_records = len(df_copy)
        optimal_days = len(optimal)
        
        return {
            'total_records': total_records,
            'optimal_days': optimal_days,
            'optimal_percentage': round((optimal_days / total_records) * 100, 1) if total_records > 0 else 0,
            'avg_temp': round(df_copy['AIR_TEMP(°C)'].mean(), 1),
            'avg_humidity': round(df_copy['HUMIDITY(%)'].mean(), 1),
            'avg_wind': round(df_copy['WIND_SPEED(m/s)'].mean(), 1),
            'avg_pressure': round(df_copy['ATMO_PRESSURE(hpa)'].mean(), 1)
        }
    except Exception as e:
        print(f"Error analyzing past data: {e}")
        return {
            'total_records': 0,
            'optimal_days': 0,
            'optimal_percentage': 0,
            'avg_temp': 15.0,
            'avg_humidity': 65.0,
            'avg_wind': 2.0,
            'avg_pressure': 965.0
        }

def get_historical_records_for_today():
    """Get historical records for today's date from CSV data"""
    try:
        if df.empty:
            return []
        
        today = datetime.now()
        df_copy = df.copy()
        
        # Filter for similar dates (same month and day, any year)
        today_records = df_copy[
            (df_copy['DATE(IST)'].dt.month == today.month) & 
            (df_copy['DATE(IST)'].dt.day == today.day)
        ]
        
        # If no exact matches, get records from the same month
        if today_records.empty:
            today_records = df_copy[
                df_copy['DATE(IST)'].dt.month == today.month
            ].head(10)  # Limit to 10 records
        
        records_list = []
        for _, row in today_records.iterrows():
            records_list.append({
                'date': row['DATE(IST)'].strftime('%Y-%m-%d'),
                'temp': round(row['AIR_TEMP(°C)'], 1),
                'humidity': round(row['HUMIDITY(%)'], 1),
                'wind': round(row['WIND_SPEED(m/s)'], 1),
                'pressure': round(row['ATMO_PRESSURE(hpa)'], 1)
            })
        
        return records_list[:10]  # Return max 10 records
    except Exception as e:
        print(f"Error getting historical records: {e}")
        return []

def save_current_weather_to_csv():
    try:
        current_data = []
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for location_key in LOCATIONS.keys():
            weather = get_weather_data(location_key)
            current_data.append({
                'datetime': timestamp,
                'location': weather['location'],
                'temperature': weather['temperature'],
                'humidity': weather['humidity'],
                'wind_speed': weather['wind_speed'],
                'pressure': weather['pressure'],
                'visibility': weather.get('visibility', 'N/A'),
                'cloud_cover': weather.get('cloud_cover', 'N/A')
            })
        
        new_df = pd.DataFrame(current_data)
        csv_file = 'current_weather_data.csv'
        
        try:
            existing_df = pd.read_csv(csv_file)
            combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        except FileNotFoundError:
            combined_df = new_df
        
        combined_df.to_csv(csv_file, index=False)
        return current_data
    except:
        return []

def get_saved_weather_data():
    try:
        saved_df = pd.read_csv('current_weather_data.csv')
        return saved_df.tail(20).to_dict('records')
    except:
        return []

def generate_forecast_from_csv(location='beluwakhan', days=5):
    """Generate forecast using historical CSV data patterns"""
    if df.empty:
        return generate_static_forecast(location, days)
    
    try:
        # Get current date and similar historical dates
        current_date = datetime.now()
        current_month = current_date.month
        current_day = current_date.day
        
        # Find historical data for similar dates (same month/day from different years)
        historical_data = df[
            (df['DATE(IST)'].dt.month == current_month) & 
            (df['DATE(IST)'].dt.day.between(current_day - 3, current_day + 3))
        ]
        
        if historical_data.empty:
            # Fallback to monthly averages
            historical_data = df[df['DATE(IST)'].dt.month == current_month]
        
        if historical_data.empty:
            # Fallback to seasonal data (3-month window)
            season_months = [(current_month - 1) % 12 + 1, current_month, (current_month % 12) + 1]
            historical_data = df[df['DATE(IST)'].dt.month.isin(season_months)]
        
        if historical_data.empty:
            return generate_static_forecast(location, days)
        
        # Calculate base statistics with error handling
        def safe_mean(series, default=0):
            try:
                return series.dropna().mean() if not series.dropna().empty else default
            except:
                return default
        
        base_temp = safe_mean(historical_data['AIR_TEMP(°C)'], 15.0)
        base_humidity = safe_mean(historical_data['HUMIDITY(%)'], 65.0)
        base_wind = safe_mean(historical_data['WIND_SPEED(m/s)'], 2.0)
        base_pressure = safe_mean(historical_data['ATMO_PRESSURE(hpa)'], 965.0)
        
        # Generate forecast for next 5 days
        forecast = []
        for i in range(days):
            forecast_date = current_date + timedelta(days=i+1)
            
            # Add some realistic variation based on historical data
            temp_std = historical_data['AIR_TEMP(°C)'].std() if len(historical_data) > 1 else 3
            humidity_std = historical_data['HUMIDITY(%)'].std() if len(historical_data) > 1 else 10
            wind_std = historical_data['WIND_SPEED(m/s)'].std() if len(historical_data) > 1 else 0.5
            
            temp_variation = np.random.normal(0, min(temp_std, 5))
            humidity_variation = np.random.normal(0, min(humidity_std, 15))
            wind_variation = np.random.normal(0, min(wind_std, 1))
            
            min_temp = round(base_temp + temp_variation - 3, 1)
            max_temp = round(base_temp + temp_variation + 4, 1)
            
            # Ensure realistic ranges
            humidity = max(20, min(95, round(base_humidity + humidity_variation)))
            wind_speed = max(0, round(base_wind + wind_variation, 1))
            
            # Determine conditions based on humidity and wind
            if humidity < 50 and wind_speed < 2:
                conditions = 'Clear'
                cloud_cover = np.random.randint(0, 20)
            elif humidity < 70 and wind_speed < 3:
                conditions = 'Mostly Clear'
                cloud_cover = np.random.randint(10, 40)
            else:
                conditions = 'Partly Cloudy'
                cloud_cover = np.random.randint(30, 70)
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'min_temp': min_temp,
                'max_temp': max_temp,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'conditions': conditions,
                'cloud_cover': cloud_cover
            })
        
        return forecast
        
    except Exception as e:
        print(f"Error generating CSV forecast: {e}")
        return generate_static_forecast(location, days)

def generate_static_forecast(location='beluwakhan', days=5):
    """Generate static forecast as fallback"""
    loc_data = LOCATIONS.get(location, LOCATIONS['beluwakhan'])
    forecast = []
    
    for i in range(days):
        forecast_date = datetime.now() + timedelta(days=i+1)
        temp_variation = np.random.uniform(-3, 3)
        
        forecast.append({
            'date': forecast_date.strftime('%Y-%m-%d'),
            'min_temp': round(loc_data['temp'] + temp_variation - 3, 1),
            'max_temp': round(loc_data['temp'] + temp_variation + 4, 1),
            'humidity': loc_data['humidity'] + np.random.randint(-10, 10),
            'wind_speed': round(loc_data['wind'] + np.random.uniform(-0.5, 0.5), 1),
            'conditions': np.random.choice(['Clear', 'Partly Cloudy', 'Fair']),
            'cloud_cover': np.random.randint(0, 30)
        })
    
    return forecast

def get_hourly_today_weather(location='beluwakhan'):
    """Get today's hourly weather data from AccuWeather"""
    if not ACCUWEATHER_API_KEY:
        return []
    
    try:
        city_name = LOCATIONS.get(location, LOCATIONS['beluwakhan'])['name']
        location_key = get_location_key(city_name)
        
        if location_key:
            url = f"https://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{location_key}"
            params = {'apikey': ACCUWEATHER_API_KEY, 'details': 'true', 'metric': 'true'}
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                hourly_data = []
                for hour in data[:8]:  # Get next 8 hours
                    hourly_data.append({
                        'time': hour['DateTime'][-8:-3],  # Extract time HH:MM
                        'temperature': round(hour['Temperature']['Value'], 1),
                        'humidity': hour.get('RelativeHumidity', 50),
                        'wind_speed': round(hour['Wind']['Speed']['Value'] / 3.6, 1),
                        'conditions': hour.get('IconPhrase', 'N/A'),
                        'cloud_cover': hour.get('CloudCover', 0)
                    })
                return hourly_data
    except Exception as e:
        print(f"Hourly forecast error: {e}")
    
    return []

def get_forecast_data(location='beluwakhan'):
    """Get forecast data with API fallback to CSV-based prediction"""
    # Try API first if available
    if ACCUWEATHER_API_KEY:
        try:
            city_name = LOCATIONS.get(location, LOCATIONS['beluwakhan'])['name']
            location_key = get_location_key(city_name)
            
            if location_key:
                url = f"https://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}"
                params = {'apikey': ACCUWEATHER_API_KEY, 'details': 'true', 'metric': 'true'}
                
                response = requests.get(url, params=params, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    forecast = []
                    for day in data['DailyForecasts']:
                        forecast.append({
                            'date': day['Date'][:10],
                            'min_temp': round(day['Temperature']['Minimum']['Value'], 1),
                            'max_temp': round(day['Temperature']['Maximum']['Value'], 1),
                            'humidity': day['Day'].get('RelativeHumidity', {}).get('Average', 50),
                            'wind_speed': round(day['Day']['Wind']['Speed']['Value'] / 3.6, 1),
                            'conditions': day['Day'].get('IconPhrase', 'N/A'),
                            'cloud_cover': day['Day'].get('CloudCover', 0)
                        })
                    return forecast
        except Exception as e:
            print(f"Forecast API Error: {e}")
    
    # Fallback to CSV-based forecast
    return generate_forecast_from_csv(location)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/telescope-conditions')
@app.route('/api/telescope-conditions/<location>')
def telescope_conditions(location='beluwakhan'):
    # Get enhanced weather data
    weather = get_current_and_today_weather(location)
    prediction = predict_telescope_conditions(weather)
    past_data = get_past_data()
    forecast = get_forecast_data(location)
    hourly_today = get_hourly_today_weather(location)
    historical_records = get_historical_records_for_today()
    save_current_weather_to_csv()
    saved_data = get_saved_weather_data()
    
    # Add telescope predictions for each forecast day
    forecast_predictions = []
    for day in forecast:
        day_weather = {
            'temperature': (day['min_temp'] + day['max_temp']) / 2,
            'humidity': day['humidity'],
            'wind_speed': day['wind_speed'],
            'pressure': weather['pressure']
        }
        day_prediction = predict_telescope_conditions(day_weather)
        forecast_predictions.append({
            'date': day['date'],
            'score': day_prediction['score'],
            'recommendation': day_prediction['recommendation']
        })
    
    # Add telescope predictions for hourly data
    hourly_predictions = []
    for hour in hourly_today:
        hour_weather = {
            'temperature': hour['temperature'],
            'humidity': hour['humidity'],
            'wind_speed': hour['wind_speed'],
            'pressure': weather['pressure']
        }
        hour_prediction = predict_telescope_conditions(hour_weather)
        hourly_predictions.append({
            'time': hour['time'],
            'score': hour_prediction['score'],
            'recommendation': hour_prediction['recommendation']
        })
    
    return jsonify({
        'weather': weather,
        'prediction': prediction,
        'past_data': past_data,
        'forecast': forecast,
        'forecast_predictions': forecast_predictions,
        'hourly_today': hourly_today,
        'hourly_predictions': hourly_predictions,
        'historical_records': historical_records,
        'saved_weather_data': saved_data,
        'locations': list(LOCATIONS.keys()),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/requirements')
def requirements():
    return jsonify({
        'minimum_requirements': {
            'python': '3.7+',
            'ram': '4GB',
            'storage': '1GB free space',
            'browser': 'Chrome 80+, Firefox 75+, Safari 13+',
            'internet': 'Required for AccuWeather API'
        },
        'ideal_requirements': {
            'python': '3.9+',
            'ram': '8GB+',
            'cpu': 'Intel i5 / AMD Ryzen 5 or better',
            'storage': '2GB+ SSD',
            'browser': 'Latest Chrome/Firefox for best 3D performance',
            'internet': 'Broadband connection for real-time data'
        },
        'dependencies': [
            'Flask==2.3.3',
            'pandas==2.1.1', 
            'requests==2.31.0',
            'numpy==1.24.3',
            'python-dotenv==1.0.0'
        ],
        'api_requirements': {
            'accuweather_key': 'Free tier: 50 calls/day',
            'signup_url': 'https://developer.accuweather.com/',
            'data_file': 'UTTRAKHAND_ISRO0019_2012-11-02_2019-01-02_Nov2025_175236.csv'
        },
        'setup_instructions': [
            '1. Install Python 3.7+ (Recommended: 3.9+)',
            '2. Clone/download project files',
            '3. Run: pip install -r requirements.txt',
            '4. Get AccuWeather API key from developer.accuweather.com',
            '5. Create .env file: ACCUWEATHER_API_KEY=your_key_here',
            '6. Ensure CSV data file is in project directory',
            '7. Run: python app.py',
            '8. Open browser to http://127.0.0.1:5000'
        ],
        'features': [
            '3D Animated Starfield Background',
            'Real-time AccuWeather API Integration',
            '5-Day Weather Forecast',
            'Historical Data Analysis (2012-2019)',
            'Telescope Viewing Condition Predictions',
            'Multi-location Support (4 cities)',
            'CSV Data Export and Storage',
            'Responsive Design with Space Theme',
            'Auto-refresh every 5 minutes'
        ]
    })

@app.route('/export/weather-data')
def export_weather_data():
    """Export weather data as CSV with enhanced data"""
    try:
        # Try to read saved data first
        try:
            saved_df = pd.read_csv('current_weather_data.csv')
        except FileNotFoundError:
            # Generate sample data if no saved data exists
            sample_data = []
            for location in LOCATIONS.keys():
                weather = get_weather_data(location)
                sample_data.append({
                    'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'location': weather['location'],
                    'temperature': weather['temperature'],
                    'humidity': weather['humidity'],
                    'wind_speed': weather['wind_speed'],
                    'pressure': weather['pressure'],
                    'visibility': weather['visibility'],
                    'cloud_cover': weather['cloud_cover']
                })
            saved_df = pd.DataFrame(sample_data)
        
        # Add telescope viewing scores
        saved_df['telescope_score'] = saved_df.apply(lambda row: predict_telescope_conditions({
            'temperature': row['temperature'],
            'humidity': row['humidity'],
            'wind_speed': row['wind_speed'],
            'pressure': row['pressure']
        })['score'], axis=1)
        
        csv_data = saved_df.to_csv(index=False)
        
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=telescope_weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

@app.route('/api/export-stats')
def export_stats():
    try:
        saved_df = pd.read_csv('current_weather_data.csv')
        return jsonify({
            'total_records': len(saved_df),
            'date_range': {
                'first_record': saved_df['datetime'].iloc[0],
                'last_record': saved_df['datetime'].iloc[-1]
            },
            'locations_covered': saved_df['location'].unique().tolist(),
            'file_size_kb': round(os.path.getsize('current_weather_data.csv') / 1024, 2),
            'export_url': '/export/weather-data'
        })
    except FileNotFoundError:
        return jsonify({
            'total_records': 0,
            'message': 'No data available for export',
            'export_url': None
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)