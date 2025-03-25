# ai_functions.py
import ollama
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import re

GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME")
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")
client = ollama.Client()
model = "AI-Planner"

def get_location_info(place_name):
    try:
        response = requests.get(
            "http://api.geonames.org/searchJSON",
            params={"q": place_name, "maxRows": 1, "username": GEONAMES_USERNAME}
        )
        data = response.json()
        if data["totalResultsCount"] > 0:
            result = data["geonames"][0]
            return {
                "lat": result["lat"],
                "lng": result["lng"],
                "country": result.get("countryName", ""),
                "timezone": result.get("timezone", {}).get("timeZoneId", ""),
                "population": result.get("population", ""),
                "name": result["name"]
            }
        return None
    except Exception as e:
        print(f"Error getting location info: {e}")
        return None

# Add to ai_functions.py
def get_places_of_interest(lat, lng, radius=5000, amenity_type=None):
    """Get real places using OpenStreetMap Overpass API"""
    url = "https://overpass-api.de/api/interpreter"
    
    query = f"""
    [out:json];
    (
      node["tourism"~"hotel|guesthouse|attraction"]
        (around:{radius},{lat},{lng});
      node["amenity"~"restaurant|cafe|bar"]
        (around:{radius},{lat},{lng});
    );
    out center;
    """
    
    try:
        response = requests.post(url, data=query)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for element in data['elements']:
            if 'tags' not in element:
                continue
                
            result = {
                'id': element['id'],
                'name': element['tags'].get('name', 'Unnamed Location'),
                'type': element['tags'].get('tourism') or element['tags'].get('amenity'),
                'lat': element.get('lat'),
                'lon': element.get('lon'),
                'address': element['tags'].get('addr:street'),
                'website': element['tags'].get('website'),
                'phone': element['tags'].get('phone')
            }
            
            if amenity_type and result['type'] != amenity_type:
                continue
                
            results.append(result)
            
        return results
        
    except Exception as e:
        print(f"Overpass API error: {e}")
        return []

def get_route(start_coords, end_coords, profile='driving-car'):
    """Get route data from OpenRouteService"""
    url = "https://api.openrouteservice.org/v2/directions/" + profile
    
    headers = {
        'Authorization': OPENROUTE_API_KEY,
        'Accept': 'application/json'
    }
    
    params = {
        'start': f"{start_coords[1]},{start_coords[0]}",
        'end': f"{end_coords[1]},{end_coords[0]}"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        summary = data['features'][0]['properties']['summary']
        geometry = data['features'][0]['geometry']['coordinates']
        
        return {
            'distance': summary['distance'],
            'duration': summary['duration'],
            'coordinates': [(lon, lat) for lon, lat in geometry]
        }
        
    except Exception as e:
        print(f"OpenRouteService error: {e}")
        return None

def create_structured_itinerary(user_info, location_info):
    """Create structured itinerary with real locations and AI-enhanced planning"""
    try:
        # Validate input data
        if not location_info.get('lat') or not location_info.get('lng'):
            raise ValueError("Invalid location coordinates")

        arrival_date = parse_date(user_info['arrival_date'])
        duration = int(user_info['duration'])
        
        # Get real locations with error handling
        hotels = get_places_of_interest(
            location_info['lat'], 
            location_info['lng'],
            amenity_type='hotel'
        )[:3]  # Get top 3 hotels
        
        restaurants = get_places_of_interest(
            location_info['lat'],
            location_info['lng'],
            amenity_type='restaurant'
        )[:5]  # Get top 5 restaurants

        # Validate we found locations
        if not hotels:
            print("Warning: No hotels found in the area")
        if not restaurants:
            print("Warning: No restaurants found in the area")

        # Build structured prompt with validation
        activity_prompt = f"""
        Create a {duration}-day itinerary for {user_info['destination']} with these rules:

        FORMAT REQUIREMENTS:
        1. Each day must have morning/afternoon/evening activities
        2. Every activity must include:
           - Exact time (e.g. "9:00-11:00")
           - Location name from provided lists
           - Cost estimate in {user_info['budget'].split()[0]}
        3. Include transportation details between locations
        4. Restaurant recommendations must come from this list:
           {", ".join([r['name'] for r in restaurants])}
        5. Hotels must come from this list:
           {", ".join([h['name'] for h in hotels])}

        EXAMPLE FORMAT:
        DAY 1: Friday, July 18, 2025
        MORNING:
        - 9:00-11:00: Surf lesson at Praia do Norte (€50)
          (Transport: 10min walk from Hotel Mar Bravo)
        AFTERNOON:
        - 12:30-14:00: Lunch at Taberna D'Adélia (€25/person)
        EVENING:
        - 19:00-21:00: Dinner at Gaivota (€35/person)
        DAILY TIPS:
        - Wear reef-safe sunscreen
        - Book surf lessons in advance
        ESTIMATED DAILY COST: €110
        """

        # Generate and validate AI response
        ai_response = client.generate(model=model, prompt=activity_prompt)
        if not ai_response or not ai_response.response:
            raise ValueError("AI failed to generate itinerary")

        # Improved parsing with error recovery
        itinerary = {
            "destination": user_info['destination'],
            "country": location_info.get('country', ''),
            "budget": user_info['budget'],
            "duration": duration,
            "accommodation": {
                "type": user_info['shelter'],
                "options": hotels
            },
            "restaurants": restaurants,
            "days": parse_ai_response(ai_response.response, arrival_date, duration),
            "travel_tips": generate_travel_tips(user_info['destination'], location_info)
        }

        # Add cost validation
        total_estimated = sum(
            float(day['estimated_cost'].replace('$','').strip())
            for day in itinerary['days'] 
            if day['estimated_cost'].lower() != 'varies'
        )
        itinerary['total_estimated_cost'] = total_estimated

        for day in itinerary['days']:
            # Ensure all time slots have content
            for time_slot in ['morning', 'afternoon', 'evening']:
                if not day['activities'].get(time_slot):
                    day['activities'][time_slot] = [f"Free time to explore {user_info['destination']}"]
            
            # Format cost estimates
            if day['estimated_cost'] == "Varies":
                day['estimated_cost'] = calculate_day_cost(day)

        return itinerary

    except Exception as e:
        print(f"Error: {str(e)}")
        # Ensure hotels/restaurants exist for fallback
        hotels = hotels or [{"name": "Local Accommodation"}]
        restaurants = restaurants or [{"name": "Local Restaurant"}]
        return create_fallback_itinerary(user_info, hotels, restaurants)

def calculate_day_cost(day):
    """Estimate costs when not provided by AI"""
    base_cost = 100  # Default base cost per day
    activity_count = sum(len(day['activities'][slot]) for slot in ['morning', 'afternoon', 'evening'])
    return f"${base_cost * activity_count}"

def create_fallback_itinerary(user_info, hotels, restaurants):
    """Create basic itinerary using real data when AI generation fails"""
    arrival_date = parse_date(user_info['arrival_date'])
    duration = int(user_info['duration'])
    
    itinerary = {
        "destination": user_info['destination'],
        "country": "",
        "budget": user_info['budget'],
        "arrival_date": user_info['arrival_date'],
        "duration": duration,
        "people": user_info['people'],
        "accommodation": user_info['shelter'],
        "days": [],
        "travel_tips": [
            "We encountered issues generating your itinerary but found these real locations:",
            f"Hotels: {', '.join([h['name'] for h in hotels])}",
            f"Restaurants: {', '.join([r['name'] for r in restaurants])}"
        ]
    }

    # Create simple day structure
    for day_num in range(1, duration + 1):
        current_date = arrival_date + timedelta(days=day_num-1)
        itinerary['days'].append({
            "day_number": day_num,
            "date": current_date.strftime("%A, %B %d, %Y"),
            "activities": {
                "morning": ["Explore local attractions"],
                "afternoon": ["Lunch at recommended restaurant"],
                "evening": ["Relax at accommodation"]
            },
            "estimated_cost": "Varies"
        })
    
    return itinerary

def parse_ai_response(response, start_date, duration):
    """Parse AI response with improved error handling"""
    days = []
    current_date = start_date
    
    # Split days using regex for better reliability
    day_sections = re.split(r'DAY\s+\d+:', response)
    if not day_sections:
        day_sections = [response]  # Fallback if parsing fails

    for i in range(1, min(len(day_sections), duration + 1)):
        day_content = day_sections[i].strip()
        day_data = {
            "day_number": i,
            "date": current_date.strftime("%A, %B %d, %Y"),
            "activities": {
                "morning": [],
                "afternoon": [],
                "evening": []
            },
            "tips": [],
            "estimated_cost": "Varies"
        }

        # Use regex patterns for extraction
        patterns = {
            'morning': r'MORNING:\s*(.*?)(?=\n\s*AFTERNOON:)',
            'afternoon': r'AFTERNOON:\s*(.*?)(?=\n\s*EVENING:)', 
            'evening': r'EVENING:\s*(.*?)(?=\n\s*DAILY TIPS:)',
            'tips': r'DAILY TIPS:\s*(.*?)(?=\n\s*ESTIMATED DAILY COST:)',
            'cost': r'ESTIMATED DAILY COST:\s*([^\n]+)'
        }

        for section, pattern in patterns.items():
            match = re.search(pattern, day_content, re.DOTALL)
            if match:
                content = match.group(1).strip()
                if section == 'cost':
                    day_data['estimated_cost'] = content
                else:
                    items = [item.strip() for item in content.split('\n- ') if item.strip()]
                    if section == 'tips':
                        day_data['tips'] = items
                    else:
                        day_data['activities'][section] = items

        days.append(day_data)
        current_date += timedelta(days=1)

    return days



def generate_travel_tips(destination, location_info):
    tip_prompt = f"""
    Provide 5 essential travel tips for visiting {destination}, {location_info.get('country', '')}.
    Include information about:
    1. Local transportation
    2. Safety considerations
    3. Cultural customs
    4. Weather and what to pack
    5. Money and budgeting tips
    
    Format each tip with a title and brief description.
    """
    
    tip_response = client.generate(model=model, prompt=tip_prompt)
    
    # Process the tips
    tips = []
    for line in tip_response.response.split("\n"):
        if line.strip():
            tips.append(line.strip())
    
    return tips

def parse_date(date_string):
    try:
        return datetime.strptime(date_string, "%m/%d/%Y")
    except ValueError:
        print("Invalid date format. Using current date instead.")
        return datetime.now()
        
