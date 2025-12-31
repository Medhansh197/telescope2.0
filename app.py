from flask import Flask, render_template, jsonify, Response
import requests
from datetime import datetime, timedelta
import os
import random
import csv
import io

app = Flask(__name__)

LOCATIONS = {
    'beluwakhan': {'name': 'Beluwakhan', 'temp': 15.2, 'humidity': 65, 'wind': 2.1, 'pressure': 965.5},
    'nainital': {'name': 'Nainital', 'temp': 12.8, 'humidity': 58, 'wind': 1.8, 'pressure': 967.2},
    'delhi': {'name': 'Delhi', 'temp': 22.5, 'humidity': 72, 'wind': 3.2, 'pressure': 1013.2},
    'mumbai': {'name': 'Mumbai', 'temp': 28.1, 'humidity': 78, 'wind': 2.8, 'pressure': 1012.8}
}

def get_weather_data(location='beluwakhan'):
    loc_data = LOCATIONS.get(location, LOCATIONS['beluwakhan'])
    current_hour = datetime.now().hour
    temp_modifier = random.uniform(0, 4) if 6 <= current_hour <= 18 else random.uniform(-4, 0)
    
    return {
        'location': loc_data['name'],
        'current_time': datetime.now().isoformat(),
        'temperature': round(loc_data['temp'] + temp_modifier, 1),
        'feels_like': round(loc_data['temp'] + temp_modifier + random.uniform(-2, 2), 1),
        'humidity': max(20, min(90, loc_data['humidity'] + random.randint(-10, 10))),
        'wind_speed': round(loc_data['wind'] + random.uniform(-0.8, 0.8), 1),
        'wind_direction': random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']),
        'pressure': round(loc_data['pressure'] + random.uniform(-3, 3), 1),
        'visibility': random.choice([8, 10, 12, 15]),
        'cloud_cover': random.randint(0, 60),
        'weather_text': random.choice(['Clear', 'Partly Cloudy', 'Fair']),
        'uv_index': max(0, min(10, random.randint(0, 8) if 6 <= current_hour <= 18 else 0)),
        'today_min_temp': round(loc_data['temp'] + temp_modifier - 6, 1),
        'today_max_temp': round(loc_data['temp'] + temp_modifier + 4, 1),
        'today_day_conditions': random.choice(['Fair', 'Partly Cloudy', 'Mostly Sunny']),
        'today_night_conditions': random.choice(['Clear', 'Partly Cloudy', 'Fair']),
        'sunrise': '06:30',
        'sunset': '18:00',
        'moon_phase': ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'][datetime.now().day % 8],
        'api_source': 'Live Simulation Data'
    }

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
    
    recommendation = "Excellent" if score >= 75 else "Good" if score >= 50 else "Poor"
    
    return {'score': score, 'recommendation': recommendation, 'factors': factors}

def get_forecast_data(location='beluwakhan', days=5):
    loc_data = LOCATIONS.get(location, LOCATIONS['beluwakhan'])
    forecast = []
    
    for i in range(days):
        forecast_date = datetime.now() + timedelta(days=i+1)
        temp_variation = random.uniform(-3, 3)
        
        forecast.append({
            'date': forecast_date.strftime('%Y-%m-%d'),
            'min_temp': round(loc_data['temp'] + temp_variation - 3, 1),
            'max_temp': round(loc_data['temp'] + temp_variation + 4, 1),
            'humidity': max(20, min(90, loc_data['humidity'] + random.randint(-10, 10))),
            'wind_speed': round(loc_data['wind'] + random.uniform(-0.5, 0.5), 1),
            'conditions': random.choice(['Clear', 'Partly Cloudy', 'Fair']),
            'cloud_cover': random.randint(0, 30)
        })
    
    return forecast

def get_past_data():
    return {
        'total_records': 2847,
        'optimal_days': 892,
        'optimal_percentage': 31.3,
        'avg_temp': 15.2,
        'avg_humidity': 65.4,
        'avg_wind': 2.1,
        'avg_pressure': 965.8
    }

def get_hourly_data(location='beluwakhan'):
    hourly = []
    for i in range(8):
        hour_time = (datetime.now() + timedelta(hours=i)).strftime('%H:%M')
        weather = get_weather_data(location)
        hourly.append({
            'time': hour_time,
            'temperature': weather['temperature'] + random.uniform(-2, 2),
            'humidity': weather['humidity'] + random.randint(-5, 5),
            'wind_speed': weather['wind_speed'] + random.uniform(-0.5, 0.5),
            'conditions': random.choice(['Clear', 'Fair', 'Partly Cloudy']),
            'cloud_cover': random.randint(0, 40)
        })
    return hourly

def get_historical_records():
    records = []
    for i in range(5):
        date = datetime.now() - timedelta(days=365*i)
        records.append({
            'date': date.strftime('%Y-%m-%d'),
            'temp': round(15.2 + random.uniform(-5, 5), 1),
            'humidity': random.randint(45, 75),
            'wind': round(2.1 + random.uniform(-1, 1), 1),
            'pressure': round(965.5 + random.uniform(-10, 10), 1)
        })
    return records

def get_saved_weather_data():
    saved_data = []
    for i in range(10):
        timestamp = datetime.now() - timedelta(hours=i)
        for loc_key, loc_data in LOCATIONS.items():
            saved_data.append({
                'datetime': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'location': loc_data['name'],
                'temperature': round(loc_data['temp'] + random.uniform(-3, 3), 1),
                'humidity': loc_data['humidity'] + random.randint(-10, 10),
                'wind_speed': round(loc_data['wind'] + random.uniform(-0.5, 0.5), 1),
                'pressure': round(loc_data['pressure'] + random.uniform(-5, 5), 1),
                'visibility': random.choice([8, 10, 12, 15]),
                'cloud_cover': random.randint(0, 50)
            })
    return saved_data[:20]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/telescope-conditions')
@app.route('/api/telescope-conditions/<location>')
def telescope_conditions(location='beluwakhan'):
    weather = get_weather_data(location)
    prediction = predict_telescope_conditions(weather)
    past_data = get_past_data()
    forecast = get_forecast_data(location)
    hourly_today = get_hourly_data(location)
    historical_records = get_historical_records()
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

@app.route('/export/weather-data')
def export_weather_data():
    """Export weather data as CSV"""
    try:
        saved_data = get_saved_weather_data()
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['datetime', 'location', 'temperature', 'humidity', 'wind_speed', 'pressure', 'visibility', 'cloud_cover'])
        writer.writeheader()
        writer.writerows(saved_data)
        
        csv_data = output.getvalue()
        output.close()
        
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=telescope_weather_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
        )
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)