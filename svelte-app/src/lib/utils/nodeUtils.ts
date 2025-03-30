// src/lib/utils/nodeUtils.ts
import type { SiloNode, SiloEdge} from '$lib/stores/siloStore';
import { NODE_TYPES } from '$lib/stores/nodeTypes';
import type { NodeType } from '$lib/types/nodes';
import type { Position } from '$lib/stores/siloStore';

// Connection path calculation (curved lines)
export function calculateConnectionPath(start: Position, end: Position) {
  const midX = (start.x + end.x) / 2;
  const midY = (start.y + end.y) / 2;
  return `M${start.x},${start.y} 
          Q${midX},${start.y} ${midX},${midY}
          T${end.x},${end.y}`;
}
export const VALID_CONNECTIONS: Record<NodeType, NodeType[]> = {
  itinerary: ['day'],
  day: ['transport', 'restaurant', 'hotel', 'activity', 'landmark'],
  transport: ['day', 'restaurant', 'hotel'],
  restaurant: ['day', 'transport'],
  hotel: ['day', 'transport'],
  activity: ['day'],
  landmark: ['day'],
  output: []
};
// Connection validation rules
export function validateConnection(sourceType: NodeType, targetType: NodeType) {
    return VALID_CONNECTIONS[sourceType].includes(targetType);
  }

// Grid snapping
export function snapToGrid(position: { x: number; y: number }, gridSize = 20): { x: number; y: number } {
  return {
    x: Math.round(position.x / gridSize) * gridSize,
    y: Math.round(position.y / gridSize) * gridSize
  };
}

// Get node symbol/icon
export function getNodeSymbol(nodeType: NodeType): string {
  return NODE_TYPES[nodeType]?.icon || '⭕';
}

// Find connections for a node
export function getNodeConnections(nodeId: string, edges: SiloEdge[]): SiloEdge[] {
  return edges.filter(
    edge => edge.source === nodeId || edge.target === nodeId
  );
}

// Error formatting for connection validation
export function formatConnectionError(error: { isValid: boolean; message?: string }, nodes: SiloNode[]): string {
  if (!error.message) return '';
  
  // Add AI suggestions for common errors
  const suggestions: Record<string, string> = {
    'restaurant-transport': 'Try adding a transportation node between restaurant and activity',
    'hotel-day': 'Connect hotel to a specific day node',
    'output-itinerary': 'Output should connect directly to the main itinerary node'
  };

  const suggestionKey = `${error.message.split(' ')[2]}-${error.message.split(' ')[4]}`;
  return `${error.message}. ${suggestions[suggestionKey] || ''}`;
}

// Calculate node position for new connections
export function getNewNodePosition(existingNodes: SiloNode[], gridSize = 20): { x: number; y: number } {
  const baseX = 100;
  const baseY = 100;
  const spacing = 200;

  // Find rightmost node position
  const maxX = existingNodes.reduce((max, node) => Math.max(max, node.position.x), baseX);
  
  return snapToGrid({
    x: maxX + spacing,
    y: baseY + (existingNodes.length % 3) * spacing
  }, gridSize);
}