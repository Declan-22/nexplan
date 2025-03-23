export interface UserInfo {
  destination: string;
  budget: string;
  arrival_date: string;
  duration: string;
  shelter: string;  // Keep as shelter for frontend
  people: string;
  activities: string;
  transportation: string;
  special_interests: string;
}
  
  export interface LocationInfo {
    lat?: string;
    lng?: string;
    country?: string;
    timezone?: string;
    population?: string;
    name: string;
  }
  
  export interface DayActivity {
    morning: string[];
    afternoon: string[];
    evening: string[];
    tips?: string[];
  }
  
export interface ItineraryDay {
    day_number: number;
    date: string;
    title?: string; // Optional property
    activities: {
        morning: string[];
        afternoon: string[];
        evening: string[];
        tips?: string[]; // Optional property
    };
    estimated_cost?: string; // Optional property
}
  
  export interface Itinerary {
    id?: string;
    user_id?: string;
    destination: string;
    country?: string;
    budget: string;
    arrival_date: string;
    duration: string | number;
    people: string;
    accommodation: string;
    days: ItineraryDay[];
    travel_tips: string[];
    created_at?: string;
  }