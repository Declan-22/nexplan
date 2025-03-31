import type { SiloNode, SiloEdge, Position } from '$lib/stores/siloStore';
import { NODE_TYPES } from '$lib/types/nodes';
import type { NodeType } from '$lib/types/nodes';

// Bezier curve connection path calculation for smooth connections
export function calculateConnectionPath(start: Position, end: Position) {
  const dx = end.x - start.x;
  const dy = end.y - start.y;
  const curvature = Math.min(Math.max(Math.abs(dx) * 0.25, 50), 150);
  
  return `M ${start.x} ${start.y}
          C ${start.x + curvature} ${start.y},
            ${end.x - curvature} ${end.y},
            ${end.x} ${end.y}`;
}

// Connection validation rules
export const VALID_CONNECTIONS: Record<NodeType, NodeType[]> = {
  itinerary: ['day', 'output'],
  day: ['transport', 'restaurant', 'hotel', 'activity', 'landmark'],
  transport: ['restaurant', 'hotel', 'activity', 'landmark', 'day'],
  restaurant: ['transport', 'activity', 'day'],
  hotel: ['transport', 'day'],
  activity: ['transport', 'restaurant', 'day'],
  landmark: ['transport', 'day'],
  output: []
};

// Validate if a connection between two node types is valid
export function validateConnection(sourceType: NodeType, targetType: NodeType): boolean {
  return VALID_CONNECTIONS[sourceType]?.includes(targetType) || false;
}

// Determine the validation status of a node (e.g., if it has required connections)
export function validateNodeConnections(node: SiloNode, edges: SiloEdge[], nodes: SiloNode[]): ValidationResult {
  const nodeConnections = edges.filter(edge => 
    edge.source === node.id || edge.target === node.id
  );
  
  const connectedNodeTypes = nodeConnections.map(edge => {
    const connectedId = edge.source === node.id ? edge.target : edge.source;
    const connectedNode = nodes.find(n => n.id === connectedId);
    return connectedNode?.type;
  }).filter(Boolean) as NodeType[];
  
  const result: ValidationResult = {
    isValid: true,
    missingConnections: []
  };
  
  // Different nodes have different validation requirements
  if (node.type === 'activity') {
    if (!connectedNodeTypes.includes('transport')) {
      result.isValid = false;
      result.missingConnections.push('transport');
    }
  } else if (node.type === 'restaurant') {
    if (!connectedNodeTypes.includes('transport') && !connectedNodeTypes.some(type => ['day', 'activity'].includes(type))) {
      result.isValid = false;
      result.missingConnections.push('transport');
    }
  } else if (node.type === 'hotel') {
    if (!connectedNodeTypes.includes('transport') && !connectedNodeTypes.includes('day')) {
      result.isValid = false;
      result.missingConnections.push('transport');
    }
  }
  
  return result;
}

export interface ValidationResult {
  isValid: boolean;
  missingConnections: NodeType[];
}

// Grid snapping with improved usability
export function snapToGrid(position: Position, gridSize = 20): Position {
  return {
    x: Math.round(position.x / gridSize) * gridSize,
    y: Math.round(position.y / gridSize) * gridSize
  };
}

// Find optimal position for a new node
export function getOptimalNodePosition(nodes: SiloNode[], viewportWidth?: number, viewportHeight?: number): Position {
  if (nodes.length === 0) {
    return { x: 200, y: 200 };
  }
  
  // Find the rightmost and bottommost nodes
  const maxX = Math.max(...nodes.map(n => n.position.x));
  const maxY = Math.max(...nodes.map(n => n.position.y));
  
  // If we have many nodes in a row, start a new column
  const nodesAtMaxX = nodes.filter(n => Math.abs(n.position.x - maxX) < 50).length;
  
  if (nodesAtMaxX > 2 || (viewportWidth && maxX > viewportWidth - 300)) {
    // Start a new column
    const minX = Math.min(...nodes.map(n => n.position.x));
    return { x: minX, y: maxY + 200 };
  }
  
  // Otherwise, add to the right
  return { x: maxX + 250, y: nodes[nodes.length - 1].position.y };
}