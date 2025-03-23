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
def get_places_of_interest(location, query):
    """Get real places using OpenStreetMap"""
    url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json];
    area[name="{location}"]->.searchArea;
    (
      node["tourism"~"hotel|guesthouse|attraction"](area.searchArea);
      way["amenity"~"restaurant|cafe"](area.searchArea);
    );
    out center;
    """
    response = requests.post(url, data=query)
    return response.json()

def create_structured_itinerary(user_info, location_info):
    arrival_date = parse_date(user_info['arrival_date'])
    duration = int(user_info['duration'])
    
    # Create a day-by-day itinerary structure
    itinerary = {
        "destination": user_info['destination'],
        "country": location_info.get('country', ''),
        "budget": user_info['budget'],
        "arrival_date": user_info['arrival_date'],
        "duration": duration,
        "people": user_info['people'],
        "accommodation": user_info['shelter'],
        "days": []
    }
    
    # Generate activities based on user preferences
    activities = user_info['activities'].split(',')
    
    # Create a prompt for the AI model to generate detailed day plans
    activity_prompt = f"""
    Create a {duration}-day travel itinerary for {user_info['destination']} with a budget of {user_info['budget']}.
    The travelers are {user_info['people']} people interested in {user_info['activities']}.
    They'll be staying in a {user_info['shelter']}.
    
    Format each day with specific morning, afternoon, and evening activities.
    Include estimated costs for each activity, transportation tips, and local recommendations.
    Include at least one must-see attraction each day and one local food experience.
    
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
