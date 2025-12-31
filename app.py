from flask import Flask, render_template, jsonify
import requests
from datetime import datetime, timedelta
import os
import random

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
        'humidity': loc_data['humidity'] + random.randint(-10, 10),
        'wind_speed': round(loc_data['wind'] + random.uniform(-0.8, 0.8), 1),
        'pressure': round(loc_data['pressure'] + random.uniform(-3, 3), 1),
        'visibility': random.choice([8, 10, 12, 15]),
        'cloud_cover': random.randint(0, 60),
        'weather_text': random.choice(['Clear', 'Partly Cloudy', 'Fair']),
        'api_source': 'Simulation Data'
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
            'humidity': loc_data['humidity'] + random.randint(-10, 10),
            'wind_speed': round(loc_data['wind'] + random.uniform(-0.5, 0.5), 1),
            'conditions': random.choice(['Clear', 'Partly Cloudy', 'Fair']),
            'cloud_cover': random.randint(0, 30)
        })
    
    return forecast

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/telescope-conditions')
@app.route('/api/telescope-conditions/<location>')
def telescope_conditions(location='beluwakhan'):
    weather = get_weather_data(location)
    prediction = predict_telescope_conditions(weather)
    forecast = get_forecast_data(location)
    
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
    
    return jsonify({
        'weather': weather,
        'prediction': prediction,
        'forecast': forecast,
        'forecast_predictions': forecast_predictions,
        'locations': list(LOCATIONS.keys()),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)