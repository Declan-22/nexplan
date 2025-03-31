import { writable, derived } from 'svelte/store';
import type { Position } from '$lib/stores/siloStore';

interface DragState {
  isDragging: boolean;
  nodeId: string | null;
  startPosition: Position | null;
  currentPosition: Position | null;
  offset: Position | null;
}

const initialDragState: DragState = {
  isDragging: false,
  nodeId: null,
  startPosition: null,
  currentPosition: null,
  offset: null
};

export const dragStore = writable<DragState>(initialDragState);

export const isDragging = derived(dragStore, ($state) => $state.isDragging);

export function startDrag(nodeId: string, startPosition: Position, offset: Position) {
  dragStore.update(state => ({
    ...state,
    isDragging: true,
    nodeId,
    startPosition,
    currentPosition: startPosition,
    offset
  }));
}

export function updateDragPosition(position: Position) {
  dragStore.update(state => ({
    ...state,
    currentPosition: position
  }));
}

export function endDrag() {
  dragStore.set(initialDragState);
}