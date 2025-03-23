from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # import CORS
from supabase import create_client, Client
from ai_functions import get_location_info, create_structured_itinerary
import os
import uuid
import json
from datetime import datetime, timedelta

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app, origins="*")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Setup Supabase connection
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def log_to_supabase(log_message: str):
    try:
        print(f"Attempting to log: {log_message}")
        # Generate a UUID for user_id
        log_user_id = str(uuid.uuid4())
        response = supabase.table('logs').insert({
            "message": log_message,
            "user_id": log_user_id  # Use a valid UUID
        }).execute()
        print(f"Supabase response: {response}")
    except Exception as e:
        print(f"Supabase log error: {str(e)}")

@app.route('/')
def health_check():
    return jsonify({"status": "healthy", "message": "API is running"})

@app.route('/api/gather_info', methods=['POST'])
def gather_user_info():
    data = request.get_json()
    if data:
        log_to_supabase(f"User info gathered: {data}")
        return jsonify({"status": "success", "message": "User info gathered successfully"})
    else:
        log_to_supabase("Failed to gather user info")
        return jsonify({"status": "error", "message": "Failed to gather user info"}), 400

@app.route('/api/itinerary', methods=['POST'])
def create_itinerary():
    try:
        user_info = request.get_json()
        if not user_info:
            return jsonify({"error": "No user information provided"}), 400

        destination = user_info.get('destination', 'Unknown Destination')
        budget = user_info.get('budget', 'Unknown Budget')
        itinerary_id = str(uuid.uuid4())

        # Get real location info
        location_info = get_location_info(destination)
        if not location_info:
            location_info = {"name": destination}

        # Create the itinerary using AI
        itinerary_data = create_structured_itinerary(user_info, location_info)

        # Store in Supabase
        response = supabase.table('itineraries').insert({
            "id": itinerary_id,
            "itinerary_data": json.dumps(itinerary_data),  # Convert to JSON string
            "destination": destination,
            "budget": budget,
            "created_at": datetime.now().isoformat()
        }).execute()

        return jsonify({
            "id": itinerary_id,
            "itinerary": itinerary_data
        })

    except Exception as e:
        error_msg = f"Error creating itinerary: {str(e)}"
        print(error_msg)
        log_to_supabase(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/api/itinerary/<itinerary_id>', methods=['GET'])
def get_itinerary(itinerary_id):
    try:
        print(f"Attempting to get itinerary with ID: {itinerary_id}")
        # Fetch the itinerary from Supabase
        response = supabase.table('itineraries').select('itinerary_data').eq('id', itinerary_id).execute()
        
        print(f"Response from Supabase: {response}")
        
        if not response.data or len(response.data) == 0:
            return jsonify({"error": "Itinerary not found"}), 404
            
        # Access the itinerary_data directly without parsing
        itinerary_data = json.loads(response.data[0]['itinerary_data'])
        
        return jsonify(itinerary_data)
        
    except Exception as e:
        error_msg = f"Error retrieving itinerary: {str(e)}"
        print(error_msg)
        log_to_supabase(error_msg)
        return jsonify({"error": error_msg}), 500

@app.route('/api/itinerary/<itinerary_id>', methods=['PUT'])
def update_itinerary(itinerary_id):
    try:
        data = request.get_json()
        modification = data.get('modification', '')
        
        if not modification:
            return jsonify({"error": "No modification specified"}), 400
            
        # Fetch existing itinerary
        response = supabase.table('itineraries').select('*').eq('id', itinerary_id).execute()
        
        if not response.data:
            return jsonify({"error": "Itinerary not found"}), 404
            
        current_data = response.data[0]
        
        # Build AI prompt
        update_prompt = f"""
        CURRENT ITINERARY:
        {json.dumps(current_data['itinerary_data'])}
        
        USER REQUEST:
        {modification}
        
        RULES:
        1. Keep existing correct info
        2. Fix any geographical errors
        3. Never add fictional places
        4. Ask clarifying questions if request is unclear
        """
        
        # Get AI update
        # Assuming these are defined elsewhere in your code
        from ai_functions import get_ai_response
        ai_response = get_ai_response(update_prompt)
        
        # Process response
        updated_itinerary = json.loads(ai_response)
        
        # Update database
        supabase.table('itineraries').update({
            "itinerary_data": updated_itinerary
        }).eq('id', itinerary_id).execute()
        
        return jsonify(updated_itinerary)
        
    except Exception as e:
        error_msg = f"Error updating itinerary: {str(e)}"
        log_to_supabase(error_msg)
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)