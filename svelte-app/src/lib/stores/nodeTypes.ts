// src/lib/stores/nodeTypes.ts
export type NodeType = 'itinerary' | 'day' | 'transport' | 'restaurant' | 'hotel' | 'activity' | 'landmark' | 'output';

export interface NodeStyle {
  icon: string;
  color: string;
  bgClass: string;
}

export const NODE_TYPES: Record<NodeType, NodeStyle> = {
  itinerary: { icon: '📅', color: '#3B82F6', bgClass: 'bg-blue-100' },
  day: { icon: '📌', color: '#10B981', bgClass: 'bg-green-100' },
  transport: { icon: '🚗', color: '#8B5CF6', bgClass: 'bg-purple-100' },
  restaurant: { icon: '🍽️', color: '#EF4444', bgClass: 'bg-red-100' },
  hotel: { icon: '🏨', color: '#F59E0B', bgClass: 'bg-yellow-100' },
  activity: { icon: '🎡', color: '#EC4899', bgClass: 'bg-pink-100' },
  landmark: { icon: '🏛️', color: '#14B8A6', bgClass: 'bg-teal-100' },
  output: { icon: '📤', color: '#64748B', bgClass: 'bg-gray-100' }
};