import { writable } from 'svelte/store';
import { v4 as uuidv4 } from 'uuid';
import type { NodeType, NodeData } from '$lib/types/nodes';
import { browser } from '$app/environment';

export type Position = { x: number; y: number };
type SiloNodeId = string;

export interface SiloNode {
  id: SiloNodeId;
  type: NodeType;
  position: Position;
  data: NodeData;
  siloId: string;
}

export interface SiloEdge {
  id: string;
  source: SiloNodeId;
  target: SiloNodeId;
  siloId: string;
}

export interface Silo {
  id: string;
  name: string;
  nodes: SiloNode[];
  edges: SiloEdge[];
}

const initialSilos = browser 
  ? JSON.parse(localStorage.getItem('silos') || '[]')
  : [];

export const siloStore = writable<Silo[]>(initialSilos);

if (browser) {
  siloStore.subscribe(value => {
    localStorage.setItem('silos', JSON.stringify(value));
  });
}



siloStore.subscribe(value => {
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem('silos', JSON.stringify(value));
  }
});

export function initializeSilos() {
  if (initialSilos.length === 0) {
    siloStore.set([createDefaultSilo()]);
  }
}

function createDefaultSilo(): Silo {
  const siloId = uuidv4();
  return {
    id: siloId,
    name: 'My First Trip',
    nodes: [{
      id: 'root',
      type: 'itinerary',
      position: { x: 100, y: 100 },
      data: { title: 'My Trip' },
      siloId
    }],
    edges: []
  };
}

export function createNode(type: NodeType, siloId: string, position: Position) {
  return {
    id: crypto.randomUUID(),
    type,
    position,
    data: { title: type.charAt(0).toUpperCase() + type.slice(1) }, // "Restaurant" instead of "New Restaurant"
    siloId
  };
}

export function createEdge(source: string, target: string, siloId: string): SiloEdge {
  return {
    id: crypto.randomUUID(),
    source,
    target,
    siloId
  };
}

export function getNodePosition(siloId: string, nodeId: string): Position | undefined {
  let position: Position | undefined;
  siloStore.update(store => {
    const silo = store.find(s => s.id === siloId);
    const node = silo?.nodes.find(n => n.id === nodeId);
    position = node?.position;
    return store;
  });
  return position;
}

export function addNode(siloId: string, type: NodeType, position: Position): SiloNode {
  const newNode = createNode(type, siloId, position);
  siloStore.update(store => store.map(silo => 
    silo.id === siloId ? { ...silo, nodes: [...silo.nodes, newNode] } : silo
  ));
  return newNode;
}

export function updateNodePosition(siloId: string, nodeId: string, position: Position) {
  siloStore.update(store => store.map(silo => 
    silo.id === siloId ? {
      ...silo,
      nodes: silo.nodes.map(n => n.id === nodeId ? { ...n, position } : n)
    } : silo
  ));
}

export function deleteSilo(siloId: string) {
  siloStore.update(store => store.filter(s => s.id !== siloId));
}

export function renameSilo(siloId: string, newName: string) {
  siloStore.update(store => 
    store.map(s => s.id === siloId ? {...s, name: newName} : s)
  );
}

export function deleteNode(siloId: string, nodeId: string) {
  siloStore.update(store => 
    store.map(silo => 
      silo.id === siloId ? {
        ...silo,
        nodes: silo.nodes.filter(n => n.id !== nodeId),
        edges: silo.edges.filter(e => 
          e.source !== nodeId && e.target !== nodeId
        )
      } : silo
    )
  );
}

export function renameNode(siloId: string, nodeId: string, newTitle: string) {
  siloStore.update(store => 
    store.map(silo => 
      silo.id === siloId ? {
        ...silo,
        nodes: silo.nodes.map(n => 
          n.id === nodeId ? {...n, data: {...n.data, title: newTitle}} : n
        )
      } : silo
    )
  );
}

export function createConnection(source: string, target: string, siloId: string) {
  const newEdge = createEdge(source, target, siloId);
  siloStore.update(store => 
    store.map(silo => 
      silo.id === siloId ? { ...silo, edges: [...silo.edges, newEdge] } : silo
    )
  );
}