import { writable, get, derived } from 'svelte/store';
import type { NodeType, NodeData } from '$lib/types/nodes';
import { browser } from '$app/environment';
import { validateNodeConnections } from '$lib/utils/nodeUtils';
import { NODE_TYPES } from '$lib/types/nodes';

export type Position = { x: number; y: number };
export type SiloNodeId = string;

export interface PortPosition {
  input: Position;
  output: Position;
}

export interface ConnectionPoint {
  nodeId: string;
  portType: 'input' | 'output';
}

export interface SiloNode {
  id: SiloNodeId;
  type: NodeType;
  position: Position;
  data: NodeData;
  siloId: string;
  portPositions?: PortPosition;
  validation?: {
    isValid: boolean;
    missingConnections: NodeType[];
  };
}


export interface SiloEdge {
  id: string;
  source: SiloNodeId;
  sourceHandle?: 'input' | 'output';
  target: SiloNodeId;
  targetHandle?: 'input' | 'output';
  siloId: string;
  animated?: boolean;
}

export interface Silo {
  id: string;
  name: string;
  nodes: SiloNode[];
  edges: SiloEdge[];
  viewState?: {
    zoom: number;
    pan: Position;
  };
}

// Load from localStorage if in browser
const initialSilos = browser 
  ? JSON.parse(localStorage.getItem('silos') || '[]')
  : [];

export const siloStore = writable<Silo[]>(initialSilos);

// Save to localStorage on updates
if (browser) {
  siloStore.subscribe(value => {
    localStorage.setItem('silos', JSON.stringify(value));
  });
}

// Initialize with a default silo if none exists
export function initializeSilos() {
  const storedSilos = get(siloStore);
  if (storedSilos.length === 0) {
    const defaultSilo = createDefaultSilo();
    siloStore.set([defaultSilo]);
  }
}

function createDefaultSilo(): Silo {
  const siloId = crypto.randomUUID();
  return {
    id: siloId,
    name: 'My Trip',
    nodes: [{
      id: crypto.randomUUID(),
      type: 'itinerary',
      position: { x: 400, y: 200 },
      data: { title: 'My Trip', description: 'Plan your perfect journey' },
      siloId
    }],
    edges: [],
    viewState: {
      zoom: 1,
      pan: { x: 0, y: 0 }
    }
  };
}

// Create a new node with given type and position
export function createNode(type: NodeType, siloId: string, position: Position): SiloNode {
  const typeInfo = NODE_TYPES[type];
  return {
    id: crypto.randomUUID(),
    type,
    position,
    data: { 
      title: typeInfo.name,
      description: typeInfo.description || '' 
    },
    siloId,
    validation: {
      isValid: true,
      missingConnections: []
    }
  };
}

// Create a connection between nodes
export function createEdge(
  source: string, 
  sourceHandle: 'input' | 'output', 
  target: string, 
  targetHandle: 'input' | 'output', 
  siloId: string
): SiloEdge {
  return {
    id: crypto.randomUUID(),
    source,
    sourceHandle,
    target,
    targetHandle,
    siloId,
    animated: false
  };
}

// Get a node's position
export function getNodePosition(siloId: string, nodeId: string): Position | undefined {
  const silos = get(siloStore);
  const silo = silos.find(s => s.id === siloId);
  const node = silo?.nodes.find(n => n.id === nodeId);
  return node?.position;
}

// Add a node to a silo
export function addNode(siloId: string, type: NodeType, position: Position): SiloNode {
  const newNode = createNode(type, siloId, position);
  
  siloStore.update(store => {
    const updatedStore = store.map(silo => {
      if (silo.id !== siloId) return silo;
      
      return {
        ...silo,
        nodes: [...silo.nodes, newNode]
      };
    });
    
    return updatedStore;
  });
  
  return newNode;
}

// Update a node's position
export function updateNodePosition(siloId: string, nodeId: string, position: Position) {
  siloStore.update(store => {
    return store.map(silo => {
      if (silo.id !== siloId) return silo;
      
      const updatedNodes = silo.nodes.map(node => {
        if (node.id !== nodeId) return node;
        
        return {
          ...node,
          position: {
            x: position.x,
            y: position.y
          }
        };
      });
      
      return {
        ...silo,
        nodes: updatedNodes
      };
    });
  });
  
  // Validate connections after position update
  validateSiloNodes(siloId);
}

// Delete a silo
export function deleteSilo(siloId: string) {
  siloStore.update(store => store.filter(s => s.id !== siloId));
}

// Rename a silo
export function renameSilo(siloId: string, newName: string) {
  siloStore.update(store => 
    store.map(s => s.id === siloId ? {...s, name: newName} : s)
  );
}

// Delete a node
export function deleteNode(siloId: string, nodeId: string) {
  siloStore.update(store => 
    store.map(silo => {
      if (silo.id !== siloId) return silo;
      
      return {
        ...silo,
        nodes: silo.nodes.filter(n => n.id !== nodeId),
        edges: silo.edges.filter(e => 
          e.source !== nodeId && e.target !== nodeId
        )
      };
    })
  );
  
  // Validate remaining nodes
  validateSiloNodes(siloId);
}

// Update a node's data
export function updateNodeData(siloId: string, nodeId: string, data: Partial<NodeData>) {
  siloStore.update(store => 
    store.map(silo => {
      if (silo.id !== siloId) return silo;
      
      const updatedNodes = silo.nodes.map(node => {
        if (node.id !== nodeId) return node;
        
        return {
          ...node,
          data: {
            ...node.data,
            ...data
          }
        };
      });
      
      return {
        ...silo,
        nodes: updatedNodes
      };
    })
  );
}

// Create a connection between nodes
export function createConnection(sourceId: string, targetId: string, siloId: string) {
  siloStore.update(store => {
    const silo = store.find(s => s.id === siloId);
    if (!silo) return store;
    
    const sourceNode = silo.nodes.find(n => n.id === sourceId);
    const targetNode = silo.nodes.find(n => n.id === targetId);
    
    if (!sourceNode || !targetNode) return store;
    
    // Don't connect if source doesn't have output or target doesn't have input
    if (!shouldHaveOutputPort(sourceNode.type) || !shouldHaveInputPort(targetNode.type)) {
      return store;
    }
    
    // Validate the connection
    const isValid = validateNodeConnections(sourceNode, silo.edges, silo.nodes);
    if (!isValid) return store;
    
    // Check if this connection already exists
    const connectionExists = silo.edges.some(
      e => (e.source === sourceId && e.target === targetId) || 
           (e.source === targetId && e.target === sourceId)
    );
    
    if (connectionExists) return store;
    
    // Create the edge
    const newEdge = createEdge(
      sourceId, 
      'output', 
      targetId, 
      'input', 
      siloId
    );
    
    return store.map(s => {
      if (s.id !== siloId) return s;
      
      return {
        ...s,
        edges: [...s.edges, newEdge]
      };
    });
  });
  
  // Validate nodes after connection
  validateSiloNodes(siloId);
}

export const validationErrors = derived(siloStore, ($silos: Silo[]) => {
  const errors: Record<string, string[]> = {};
  
  $silos.forEach((silo: Silo) => {
    silo.nodes.forEach((node: SiloNode) => {
      if (node.type === 'activity') {
        const hasTransport = silo.edges.some((e: SiloEdge) => 
          e.target === node.id && silo.nodes.find((n: SiloNode) => n.id === e.source)?.type === 'transport'
        );
        
        if (!hasTransport) {
          errors[node.id] = ['Missing transportation connection'];
        }
      }
    });
  });
  
  return errors;
});

// Remove a connection
export function removeConnection(siloId: string, edgeId: string) {
  siloStore.update(store => 
    store.map(silo => {
      if (silo.id !== siloId) return silo;
      
      return {
        ...silo,
        edges: silo.edges.filter(e => e.id !== edgeId)
      };
    })
  );
  
  // Validate nodes after removing connection
  validateSiloNodes(siloId);
}

// Update port positions for a node
export function updateNodePortPositions(siloId: string, nodeId: string, portPositions: PortPosition) {
  siloStore.update(store => 
    store.map(silo => {
      if (silo.id !== siloId) return silo;
      
      const updatedNodes = silo.nodes.map(node => {
        if (node.id !== nodeId) return node;
        
        return {
          ...node,
          portPositions
        };
      });
      
      return {
        ...silo,
        nodes: updatedNodes
      };
    })
  );
}

// Validate all nodes in a silo
export function validateSiloNodes(siloId: string) {
  siloStore.update(store => {
    const silo = store.find(s => s.id === siloId);
    if (!silo) return store;
    
    const updatedNodes = silo.nodes.map(node => {
      const validation = validateNodeConnections(node, silo.edges, silo.nodes);
      
      return {
        ...node,
        validation
      };
    });
    
    return store.map(s => {
      if (s.id !== siloId) return s;
      
      return {
        ...s,
        nodes: updatedNodes
      };
    });
  });
}

// Update silo view state (pan/zoom)
export function updateSiloViewState(siloId: string, viewState: { zoom: number, pan: Position }) {
  siloStore.update(store => 
    store.map(silo => {
      if (silo.id !== siloId) return silo;
      
      return {
        ...silo,
        viewState
      };
    })
  );
}

export function shouldHaveInputPort(type: NodeType): boolean {
  return type !== 'itinerary'; // Itinerary nodes don't have input ports
}

export function shouldHaveOutputPort(type: NodeType): boolean {
  return type !== 'output'; // Output nodes don't have output ports
}