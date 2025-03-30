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
}

export const NODE_TYPES: Record<NodeType, NodeStyle> = {
  itinerary: { 
    icon: '📅', 
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