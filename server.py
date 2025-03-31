from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # import CORS
from supabase import create_client, Client
from ai_functions import get_location_info, create_structured_itinerary
import os
import uuid
import json
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__, static_folder='../svelte-app/build', static_url_path='')
CORS(app, 
     origins=["http://localhost:5173", "https://nexplan-wvdf.onrender.com/", "http://nexplan-wvdf.onrender.com/api"],
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
# Setup Supabase connection
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def json_serialize(obj):
    """
    Custom JSON serializer to handle non-serializable objects
    """
    try:
        return json.dumps(obj)
    except TypeError:
        # If standard serialization fails, convert to string
        return str(obj)

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



# Add these routes to server.py
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        return jsonify({
            "status": "success",
            "user": response.user.dict(),
            "session": response.session.dict()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']
        
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return jsonify({
            "status": "success",
            "user": response.user.dict(),
            "session": response.session.dict()
        })
    
    except Exception as e:
        return jsonify({"error": "Invalid credentials"}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        supabase.auth.sign_out()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/auth/session', methods=['GET'])
def get_session():
    try:
        session = supabase.auth.get_session()
        return jsonify({
            "status": "success",
            "user": session.user.dict() if session else None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

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
def generate_itinerary():
    logging.info("Received a request for itinerary generation")

    try:
        data = request.get_json()
        logging.debug(f"Request data: {data}")

        if not data:
            logging.error("Empty or invalid JSON payload received")
            return jsonify({"error": "Invalid request data"}), 400
    except Exception as e:
        logging.exception("Error parsing JSON request")
        return jsonify({"error": "Invalid JSON format"}), 400

    logging.info("Calling AI to generate structured itinerary...")
    response_data = create_structured_itinerary(data)


    
    print("Full request headers:", request.headers)
    print("Request content type:", request.content_type)
    try:
        # Explicitly log the incoming request data
        raw_data = request.get_data(as_text=True)
        print(f"Received raw data: {raw_data}")

        
        
        # Try parsing JSON with error handling
        try:
            user_info = request.get_json(force=True)
        except Exception as json_error:
            print(f"JSON Parsing Error: {json_error}")
            return jsonify({
                "status": "error", 
                "message": f"Invalid JSON: {str(json_error)}"
            }), 400

        # Validate user_info
        if not user_info:
            print("No user information provided")
            return jsonify({
                "status": "error", 
                "message": "No user information provided"
            }), 400

        # Required field validation
        required_fields = ['destination', 'budget', 'arrival_date', 'duration', 'people', 'shelter', 'activities']
        for field in required_fields:
            if field not in user_info or not user_info[field]:
                print(f"Missing required field: {field}")
                return jsonify({
                    "status": "error", 
                    "message": f"Missing required field: {field}"
                }), 400

        # Rest of the code remains the same as in the previous artifact
        destination = user_info.get('destination', 'Unknown Destination')
        budget = user_info.get('budget', 'Unknown Budget')
        itinerary_id = str(uuid.uuid4())

        # Get real location info 
        try:
            location_info = get_location_info(destination) 
            if not location_info:
                log_to_supabase(f"Location info fetch failed for: {destination}")
                location_info = {"name": destination}
        except Exception as e:
            log_to_supabase(f"Location info error: {str(e)}")
            location_info = {"name": destination}

        # Create the itinerary using AI 
        try:
            logging.info("Calling Llama 3.2 to generate itinerary...")
            itinerary_data = create_structured_itinerary(user_info, location_info)
            logging.debug(f"AI response: {itinerary_data}")
        except Exception as e:
            error_msg = f"Failed to create itinerary: {str(e)}"
            log_to_supabase(error_msg)
            logging.error(error_msg)
            return jsonify({
                "status": "error", 
                "message": error_msg
            }), 500

        # Ensure itinerary_data is JSON serializable
        try:
            json.dumps(itinerary_data)
        except TypeError as e:
            error_msg = f"Itinerary data not JSON serializable: {str(e)}"
            print(error_msg)
            return jsonify({
                "status": "error", 
                "message": error_msg
            }), 500

        # Store in Supabase 
        try:
            response = supabase.table('itineraries').insert({ 
                "id": itinerary_id, 
                "itinerary_data": json_serialize(itinerary_data),
                "destination": destination, 
                "budget": budget, 
                "created_at": datetime.now().isoformat() 
            }).execute()
        except Exception as e:
            error_msg = f"Failed to store itinerary in Supabase: {str(e)}"
            log_to_supabase(error_msg)
            print(error_msg)  # Add print for immediate visibility
            return jsonify({
                "status": "error", 
                "message": error_msg
            }), 500

        # Return a consistent JSON response with debug info
        response_data = { 
            "status": "success",
            "id": itinerary_id, 
            "itinerary": itinerary_data 
        }

        print(f"Full response data: {response_data}")
        print(f"Itinerary data type: {type(itinerary_data)}")
        print(f"Itinerary data keys: {itinerary_data.keys() if isinstance(itinerary_data, dict) else 'Not a dictionary'}")
        print(f"Returning response: {json.dumps(response_data)}")
        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Unexpected error creating itinerary: {str(e)}"
        print(error_msg)
        log_to_supabase(error_msg)
        return jsonify({
            "status": "error", 
            "message": error_msg
        }), 500
    


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
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Missing authorization header"}), 401
            
        # Verify user session
        try:
            session = supabase.auth.get_session()
            if not session:
                return jsonify({"error": "Invalid session"}), 401
        except Exception as auth_error:
            return jsonify({"error": f"Auth verification failed: {str(auth_error)}"}), 401

        data = request.get_json()
        if not data or 'modification' not in data:
            return jsonify({"error": "No modification specified"}), 400
            
        # Fetch existing itinerary with proper error handling
        try:
            response = supabase.table('itineraries').select('*').eq('id', itinerary_id).execute()
            if not response.data:
                return jsonify({"error": "Itinerary not found"}), 404
            current_data = response.data[0]
        except Exception as fetch_error:
            log_to_supabase(f"Fetch error: {str(fetch_error)}")
            return jsonify({"error": "Database error"}), 500

        # Build AI prompt with validation
        try:
            current_itinerary = json.loads(current_data['itinerary_data'])
            update_prompt = f"""
            CURRENT ITINERARY:
            {json.dumps(current_itinerary, indent=2)}
            
            USER MODIFICATION REQUEST:
            {data['modification']}
            
            RULES:
            1. Maintain valid JSON structure
            2. Keep existing correct information
            3. Only use real locations from original data
            4. Preserve all original fields
            """
        except Exception as prompt_error:
            return jsonify({"error": f"Prompt construction failed: {str(prompt_error)}"}), 400

        # Get AI response with error handling
        try:
            from ai_functions import get_ai_response
            ai_response = get_ai_response(update_prompt)
            updated_itinerary = json.loads(ai_response)
        except json.JSONDecodeError:
            return jsonify({"error": "AI returned invalid JSON"}), 500
        except Exception as ai_error:
            return jsonify({"error": f"AI processing failed: {str(ai_error)}"}), 500

        # Update database with proper error handling
        try:
            update_response = supabase.table('itineraries').update({
                "itinerary_data": json.dumps(updated_itinerary),
                "updated_at": datetime.now().isoformat()
            }).eq('id', itinerary_id).execute()
            
            if not update_response.data:
                return jsonify({"error": "Update failed"}), 500
                
            return jsonify(updated_itinerary)
            
        except Exception as db_error:
            log_to_supabase(f"Database update error: {str(db_error)}")
            return jsonify({"error": "Database update failed"}), 500
            
    except Exception as e:
        log_to_supabase(f"Global update error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.after_request
def add_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)