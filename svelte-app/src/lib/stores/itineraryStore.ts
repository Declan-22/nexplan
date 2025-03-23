import { writable } from 'svelte/store';
import type { Itinerary, UserInfo } from '$lib/types/types';


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
    // Format the date from YYYY-MM-DD to MM/DD/YYYY
    const formattedInfo = { ...info };
    if (formattedInfo.arrival_date) {
      const dateParts = formattedInfo.arrival_date.split('-');
      if (dateParts.length === 3) {
        // Convert from YYYY-MM-DD to MM/DD/YYYY
        formattedInfo.arrival_date = `${dateParts[1]}/${dateParts[2]}/${dateParts[0]}`;
      }
    }
    
    const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
    const response = await fetch(`${VITE_API_URL}/itinerary`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formattedInfo)
    });
    
    // Rest of the function remains the same
    if (!response.ok) {
      throw new Error('Failed to create itinerary');
    }
    
    const data = await response.json();
    
    if (data.itinerary) {
      currentItinerary.set(data.itinerary);
      return data.id;
    }
    
    return null;
  } catch (error) {
    console.error('Error creating itinerary:', error);
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
    const response = await fetch(`/api/itinerary/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ modification })
    });
    
    if (!response.ok) {
      throw new Error('Failed to update itinerary');
    }
    
    const data = await response.json();
    currentItinerary.set(data);
    return data;
  } catch (error) {
    console.error('Error updating itinerary:', error);
    return null;
  }
}