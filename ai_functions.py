# ai_functions.py
import ollama
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

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
    """Optimized route fetching with OpenRouteService."""
    url = f"https://api.openrouteservice.org/v2/directions/{profile}"

    headers = {
        'Authorization': OPENROUTE_API_KEY,
        'Accept': 'application/json'
    }

    params = {
        'start': f"{start_coords[1]},{start_coords[0]}",
        'end': f"{end_coords[1]},{end_coords[0]}",
        'overview': 'simplified',  # Reduces response size
        'geometry_simplify': 'true'
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        summary = data['routes'][0]['summary']
        route_coords = data['routes'][0]['geometry']['coordinates']

        return {
            'distance_km': round(summary['distance'] / 1000, 2),  # Convert to km
            'duration_min': round(summary['duration'] / 60, 2),  # Convert to minutes
            'route_points': [(lon, lat) for lon, lat in route_coords[::10]]  # Reduce points density
        }

    except Exception as e:
        print(f"OpenRouteService error: {e}")
        return None


def create_structured_itinerary(user_info, location_info):
    arrival_date = parse_date(user_info['arrival_date'])
    duration = int(user_info['duration'])
    
    # Create a day-by-day itinerary structure
    itinerary = {
        "destination": str(user_info['destination']),
        "country": str(location_info.get('country', '')),
        "budget": str(user_info['budget']),
        "arrival_date": str(user_info['arrival_date']),
        "duration": int(duration),
        "people": str(user_info['people']),
        "accommodation": str(user_info['shelter']),
        "days": []
    }
    
    # Generate activities based on user preferences
    activities = user_info['activities'].split(',')

        # Get real hotels
    hotels = get_places_of_interest(
        location_info['lat'], 
        location_info['lng'],
        amenity_type='hotel'
    )[:3]  # Get top 3 hotels
    
    # Get real restaurants
    restaurants = get_places_of_interest(
        location_info['lat'],
        location_info['lng'],
        amenity_type='restaurant'
    )[:5]  # Get top 5 restaurants
    
    # Create a prompt for the AI model to generate detailed day plans
    activity_prompt = f"""
    Create a {duration}-day travel itinerary for {user_info['destination']} with a budget of {user_info['budget']}.
    The travelers are {user_info['people']} people interested in {user_info['activities']}.
    They'll be staying in a {user_info['shelter']}.
    
    Format each day with specific morning, afternoon, and evening activities.
    Include estimated costs for each activity, transportation tips, and local recommendations.
    Include at least one must-see attraction each day and one local food experience.
    
        Available Hotels:
    {json.dumps([h['name'] for h in hotels])}
    
    Recommended Restaurants:
    {json.dumps([r['name'] for r in restaurants])}
    
    Traveler Preferences:
    - Budget: {user_info['budget']}
    - Group: {user_info['people']}
    - Activities: {user_info['activities']}
    
    Requirements:
    1. Use actual hotel/restaurant names from the lists
    2. Include realistic travel times between locations
    3. Balance activities with rest time
    4. Include cost estimates

    For each day, structure the response as:
    
    DAY [number]: [date]
    
    MORNING:
    - [Activity description with cost estimate]
    - [Transportation tip]
    
    AFTERNOON:
    - [Activity description with cost estimate]
    - [Local recommendation]
    
    EVENING:
    - [Activity description with cost estimate]
    - [Food recommendation]
    
    DAILY TIPS:
    - [Practical tip for this day]
    - [Cultural insight]
    
    ESTIMATED DAILY COST: [amount]
    """
    
    # Get AI response for the structured itinerary
    ai_response = client.generate(model=model, prompt=activity_prompt)
    
    # Process and structure the AI response
    try:
        # Split the response by days
        day_sections = ai_response.response.split("DAY ")
        
        # Process each day section
        for i in range(1, len(day_sections)):
            day_content = day_sections[i].strip()
            current_date = arrival_date + timedelta(days=i-1)
            
            # Extract day information
            day_parts = {}
            
            # Try to parse the structured content
            if "MORNING:" in day_content:
                morning_content = day_content.split("MORNING:")[1].split("AFTERNOON:")[0].strip()
                day_parts["morning"] = [item.strip() for item in morning_content.split("\n- ") if item.strip()]
            
            if "AFTERNOON:" in day_content:
                afternoon_content = day_content.split("AFTERNOON:")[1].split("EVENING:")[0].strip()
                day_parts["afternoon"] = [item.strip() for item in afternoon_content.split("\n- ") if item.strip()]
            
            if "EVENING:" in day_content:
                evening_section = day_content.split("EVENING:")[1]
                evening_end = None
                
                # Find where the evening section ends
                for possible_end in ["DAILY TIPS:", "ESTIMATED DAILY COST:", "DAY "]:
                    if possible_end in evening_section:
                        if evening_end is None or evening_section.find(possible_end) < evening_section.find(evening_end):
                            evening_end = possible_end
                
                # Extract evening content
                if evening_end:
                    evening_content = evening_section.split(evening_end)[0].strip()
                else:
                    evening_content = evening_section.strip()
                
                # Process the evening activities
                evening_activities = []
                for line in evening_content.split("\n"):
                    line = line.strip()
                    if line.startswith("-") or line.startswith("*"):
                        evening_activities.append(line[1:].strip())
                    elif line and not line.startswith("**") and "Food recommendation:" not in line:
                        # Catch any non-empty lines that don't start with list markers
                        evening_activities.append(line)
                
                # Filter out empty lines and duplicates
                evening_activities = [item for item in evening_activities if item.strip()]
                day_parts["evening"] = evening_activities
            
            if "DAILY TIPS:" in day_content:
                tips_section = day_content.split("DAILY TIPS:")[1]
                if "ESTIMATED DAILY COST:" in tips_section:
                    tips_content = tips_section.split("ESTIMATED DAILY COST:")[0].strip()
                else:
                    tips_content = tips_section.strip()
                day_parts["tips"] = [item.strip() for item in tips_content.split("\n- ") if item.strip()]
            
            # Try to extract cost estimate
            cost_estimate = ""
            if "ESTIMATED DAILY COST:" in day_content:
                cost_parts = day_content.split("ESTIMATED DAILY COST:")[1].strip().split("\n")[0]
                cost_estimate = cost_parts.strip()
            
            # Create the day structure
            day_info = {
                "day_number": i,
                "date": current_date.strftime("%A, %B %d, %Y"),
                "activities": day_parts,
                "estimated_cost": cost_estimate
            }
            
            # Add the day to the itinerary
            itinerary["days"].append(day_info)
    
    except Exception as e:
        print(f"Error processing AI response: {e}")
        # Fallback to a simpler structure
        for i in range(1, duration + 1):
            current_date = arrival_date + timedelta(days=i-1)
            day_info = {
                "day_number": i,
                "date": current_date.strftime("%A, %B %d, %Y"),
                "activities": {
                    "morning": ["Explore local attractions"],
                    "afternoon": ["Enjoy local cuisine"],
                    "evening": ["Relax and experience local culture"]
                },
                "estimated_cost": "Varies"
            }
            itinerary["days"].append(day_info)
    
    # Add travel tips based on location
    itinerary["travel_tips"] = generate_travel_tips(user_info['destination'], location_info)
    
    return itinerary



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
        
