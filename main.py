import ollama
from supabase import create_client, Client
import uuid
import json
import requests
from datetime import datetime, timedelta
from ai_functions import get_location_info, create_structured_itinerary
import os

# API Keys and URLs
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
GEONAMES_USERNAME = os.getenv("GEONAMES_USERNAME")
OPENROUTE_API_KEY = os.getenv("OPENROUTE_API_KEY")

# Create a Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize the Ollama client
client = ollama.Client()

# Define the model 
model = "AI-Planner"

# Hardcoded questions
# Hardcoded questions
questions = {
    "destination": "Where are you planning to go?",
    "budget": "What is your budget range for the trip?",
    "arrival_date": "When will you be arriving? (Please provide a date mm/dd/yyyy)",
    "duration": "How many days will you be staying?",
    "shelter": "Are you looking to stay in a hotel, Airbnb, or apartment?",
    "people": "How many people are you traveling with?",
    "activities": "What activities are you interested in?"
}

# Function to get coordinates from GeoNames


# Function to save the data to Supabase
def save_itinerary_to_supabase(user_id, itinerary_data):
    # Insert the itinerary data into the Supabase 'itineraries' table
    response = supabase.table('itineraries').insert({
        "user_id": user_id,
        "destination": itinerary_data["destination"],
        "budget": itinerary_data["budget"],
        "itinerary_data": json.dumps(itinerary_data)
    }).execute()

    # Check if there is an error
    if hasattr(response, 'error') and response.error:
        print(f"Failed to save itinerary: {response.error}")
        return False
    else:
        print("Itinerary successfully saved!")
        return True

# Function to update itinerary with user modifications
def update_itinerary(user_id, user_input, current_itinerary):
    update_prompt = f"""
    The user has the following itinerary for {current_itinerary['destination']}:
    {json.dumps(current_itinerary, indent=2)}
    
    The user is requesting the following modification:
    "{user_input}"
    
    Please update the itinerary accordingly while maintaining the structured format.
    """
    
    response = client.generate(model=model, prompt=update_prompt)
    
    try:
        # Try to parse the response as JSON
        updated_itinerary = json.loads(response.response)
        return updated_itinerary
    except json.JSONDecodeError:
        # If parsing fails, use the original itinerary as a base and add the AI response as notes
        current_itinerary["modification_notes"] = response.response
        return current_itinerary

# Function to format the itinerary for display
def format_itinerary_for_display(itinerary):
    formatted = f"TRAVEL ITINERARY FOR {itinerary['destination'].upper()}, {itinerary.get('country', '').upper()}\n"
    formatted += f"Travel Dates: {itinerary['arrival_date']} for {itinerary['duration']} days\n"
    formatted += f"Budget: {itinerary['budget']}\n"
    formatted += f"Travelers: {itinerary['people']}\n"
    formatted += f"Accommodation: {itinerary['accommodation']}\n\n"
    
    for day in itinerary.get("days", []):
        formatted += f"DAY {day['day_number']}: {day['date']}\n"
        formatted += "=" * 50 + "\n"
        
        formatted += "MORNING:\n"
        for activity in day.get("activities", {}).get("morning", []):
            formatted += f"- {activity}\n"
        
        formatted += "\nAFTERNOON:\n"
        for activity in day.get("activities", {}).get("afternoon", []):
            formatted += f"- {activity}\n"
        
        formatted += "\nEVENING:\n"
        for activity in day.get("activities", {}).get("evening", []):
            formatted += f"- {activity}\n"
        
        if "tips" in day.get("activities", {}):
            formatted += "\nDAILY TIPS:\n"
            for tip in day.get("activities", {}).get("tips", []):
                formatted += f"- {tip}\n"
        
        if day.get("estimated_cost"):
            formatted += f"\nESTIMATED DAILY COST: {day['estimated_cost']}\n"
        
        formatted += "\n" + "-" * 50 + "\n\n"
    
    formatted += "TRAVEL TIPS:\n"
    for tip in itinerary.get("travel_tips", []):
        formatted += f"- {tip}\n"
    
    return formatted

# Main function to run the travel planner
def main():
    print("Welcome to the AI Travel Planner!")
    print("I can help you plan your vacation. Let's get started!")
    
    # Generate a unique user ID for each session
    user_id = str(uuid.uuid4())
    
    # Store the user's responses
    user_info = {}
    
    # Ask hardcoded questions
    for key, question in questions.items():
        response = input(f"{question} ")
        user_info[key] = response
    
    # Get location information
    print(f"Getting information about {user_info['destination']}...")
    location_info = get_location_info(user_info['destination'])
    
    if location_info:
        print(f"Found location: {location_info['name']}, {location_info.get('country', '')}")
    else:
        print(f"Could not find detailed information about {user_info['destination']}. Proceeding with basic itinerary.")
        location_info = {"name": user_info['destination']}
    
    # Create structured itinerary
    print("Creating your personalized travel itinerary...")
    itinerary = create_structured_itinerary(user_info, location_info)
    
    # Format and display the itinerary
    formatted_itinerary = format_itinerary_for_display(itinerary)
    print("\n" + "=" * 80 + "\n")
    print(formatted_itinerary)
    print("=" * 80 + "\n")
    
    # Save the generated itinerary to Supabase
    save_result = save_itinerary_to_supabase(user_id, itinerary)
    
    if save_result:
        print(f"Your itinerary has been saved! Your unique ID is: {user_id}")
    
    # Loop to continue the conversation and modify the itinerary
    current_itinerary = itinerary
    while True:
        # Get input from the user
        user_input = input("\nWould you like to modify your itinerary or add anything else? (type 'exit' to quit): ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:  # Allow user to exit the loop
            print("Thank you for using AI Travel Planner. Enjoy your trip!")
            break
        
        # Update the itinerary with user input
        print("Updating your itinerary...")
        current_itinerary = update_itinerary(user_id, user_input, current_itinerary)
        
        # Format and display the updated itinerary
        formatted_itinerary = format_itinerary_for_display(current_itinerary)
        print("\n" + "=" * 80 + "\n")
        print(formatted_itinerary)
        print("=" * 80 + "\n")
        
        # Save the updated itinerary to Supabase
        save_result = save_itinerary_to_supabase(user_id, current_itinerary)
        
        if save_result:
            print("Your updated itinerary has been saved!")

if __name__ == "__main__":
    main()