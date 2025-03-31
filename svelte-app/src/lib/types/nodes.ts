export type NodeType = 
  | 'itinerary'
  | 'day'
  | 'transport'
  | 'restaurant'
  | 'hotel'
  | 'activity'
  | 'landmark'
  | 'output';

export interface NodeStyle {

  icon: string;
  color: string;
  bgClass: string;
  borderClass: string;
  name: string;
  description?: string; // Add optional property
}

export const NODE_TYPES: Record<NodeType, NodeStyle> = {
  itinerary: { 
    icon: `<svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="none">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
          </svg>`,
    color: '#3B82F6',
    bgClass: 'bg-blue-100',
    borderClass: 'border-blue-400',
    name: 'Itinerary'
  },
  day: { 
    icon: '📌', 
    color: '#10B981',
    bgClass: 'bg-green-100',
    borderClass: 'border-green-400',
    name: 'Day'
  },
  transport: { 
    icon: '🚗', 
    color: '#8B5CF6',
    bgClass: 'bg-purple-100',
    borderClass: 'border-purple-400',
    name: 'Transport'
  },
  restaurant: { 
    icon: '🍽️', 
    color: '#EF4444',
    bgClass: 'bg-red-100',
    borderClass: 'border-red-400',
    name: 'Restaurant'
  },
  hotel: { 
    icon: '🏨', 
    color: '#F59E0B',
    bgClass: 'bg-yellow-100',
    borderClass: 'border-yellow-400',
    name: 'Hotel'
  },
  activity: { 
    icon: '🎡', 
    color: '#EC4899',
    bgClass: 'bg-pink-100',
    borderClass: 'border-pink-400',
    name: 'Activity'
  },
  landmark: { 
    icon: '🏛️', 
    color: '#14B8A6',
    bgClass: 'bg-teal-100',
    borderClass: 'border-teal-400',
    name: 'Landmark'
  },
  output: { 
    icon: '📤', 
    color: '#64748B',
    bgClass: 'bg-gray-100',
    borderClass: 'border-gray-400',
    name: 'Output'
  }
};

export interface NodeData {
  title: string;
  [key: string]: any;
}