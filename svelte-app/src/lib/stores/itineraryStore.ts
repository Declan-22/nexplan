import { writable } from 'svelte/store';
import type { Itinerary, UserInfo } from '$lib/types/types';
import { getSupabaseSession, isSessionValid } from '$lib/auth';


// Store for the current itinerary
export const currentItinerary = writable<Itinerary | null>(null);

// Store for the user information
export const userInfo = writable<UserInfo>({
  destination: '',
  budget: '',
  arrival_date: '',
  duration: '',
  shelter: '',
  people: '',
  activities: '',
  transportation: 'Own Vehicle', // Default value
  special_interests: ''
});

// Function to fetch an itinerary by ID from Supabase via Flask
export async function fetchItinerary(id: string): Promise<Itinerary | null> {
  try {
    const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
    const response = await fetch(`${VITE_API_URL}/itinerary/${id}`);
    if (!response.ok) {
      throw new Error('Failed to fetch itinerary');
    }
    const data = await response.json();
    currentItinerary.set(data);
    return data;
  } catch (error) {
    console.error('Error fetching itinerary:', error);
    return null;
  }
}

// Function to create a new itinerary
// For createItinerary, use the full URL if proxy isn't working:
export async function createItinerary(info: UserInfo): Promise<string | null> {
  try {
    // Validate required fields before sending
    const requiredFields = ['destination', 'budget', 'arrival_date', 'duration', 'people', 'shelter', 'activities'];
    for (const field of requiredFields) {
      if (!info[field as keyof UserInfo]) {
        console.error(`Missing required field: ${field}`);
        throw new Error(`Missing required field: ${field}`);
      }
    }

    // Format the date from YYYY-MM-DD to MM/DD/YYYY
    const formattedInfo = { ...info };
    if (formattedInfo.arrival_date) {
      const dateParts = formattedInfo.arrival_date.split('-');
      if (dateParts.length === 3) {
        formattedInfo.arrival_date = `${dateParts[1]}/${dateParts[2]}/${dateParts[0]}`;
      }
    }

    console.log('Sending payload:', JSON.stringify(formattedInfo, null, 2));
    
    const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
    const response = await fetch(`${VITE_API_URL}/api/itinerary`, {
      method: 'POST', 
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'  // Explicitly request JSON
      }, 
      body: JSON.stringify(formattedInfo) 
    });
    
    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));
  
  
    // Log the raw response for debugging
    const responseText = await response.text();
    console.log('Raw server response:', responseText);

    // Try to parse the response as JSON
    let data;
    try {
      data = JSON.parse(responseText);
    } catch (parseError) {
      console.error('Failed to parse JSON:', parseError);
      console.error('Response text:', responseText);
      throw new Error('Invalid JSON response from server');
    }
     
    // Check for error status in the response
    if (data.status === 'error') {
      console.error('Server returned an error:', data.message);
      throw new Error(data.message || 'Failed to create itinerary');
    }

    // Validate the response structure
    if (!data.id || !data.itinerary) {
      console.error('Incomplete response:', data);
      throw new Error('Incomplete response from server');
    }
     
    // Set the current itinerary
    currentItinerary.set(data.itinerary);
    return data.id;

  } catch (error) {
    console.error('Error creating itinerary:', error);
    
    // Optionally show a user-friendly error message
    // You might want to add a toast or error notification here
    
    return null;
  }
}

// In itineraryStore.ts
function validateForm(info: UserInfo): boolean {
  return !!(
    info.destination &&
    info.budget &&
    info.arrival_date.match(/^\d{2}\/\d{2}\/\d{4}$/) &&
    info.duration
  );
}

// Function to update an existing itinerary
export async function updateItinerary(id: string, modification: string): Promise<Itinerary | null> {
  try {
    const session = await getSupabaseSession();
    if (!session) throw new Error('Not authenticated');

    const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
    const response = await fetch(`${VITE_API_URL}/api/itinerary/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${session.access_token}`
      },
      body: JSON.stringify({ modification })
    });
    
    const responseData = await response.json();
    
    if (!response.ok) {
      throw new Error(responseData.error || 'Failed to update itinerary');
    }
    
    currentItinerary.set(responseData);
    return responseData;
// Modify the updateItinerary catch block
    } catch (error) {
      if (error instanceof Error && (error.message.includes('401') || error.message.includes('Unauthorized'))) {
        window.location.href = '/login?returnUrl=' + encodeURIComponent(window.location.pathname);
      }
      console.error('Error updating itinerary:', error);
      throw error;
    }
}