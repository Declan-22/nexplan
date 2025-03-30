<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { SiloNode } from '$lib/stores/siloStore';
  import { NODE_TYPES } from '$lib/types/nodes';

  export let node: SiloNode;
  export let selected = false;

  const dispatch = createEventDispatcher<{
    dragstart: { node: SiloNode };
    positionupdate: { x: number; y: number };
  }>();

  let offsetX = 0;
  let offsetY = 0;
  let dragging = false;

  function handleConnectionStart(e: MouseEvent) {
    console.log('Connection start initiated');
  }

  function handleConnectionEnd(e: MouseEvent) {
    console.log('Connection end initiated');
  }
  
  function handleDragStart(e: MouseEvent) {
    dragging = true;
    // Store initial positions...
    document.addEventListener('mousemove', handleDrag);
    document.addEventListener('mouseup', () => {
      dragging = false;
      document.removeEventListener('mousemove', handleDrag);
    });
  }

  function handleDrag(e: MouseEvent) {
    if (dragging) {
      // Update node position
    }
  }
    // Add connection ports

    function handleDragMove(e: MouseEvent) {
      const target = e.currentTarget as HTMLElement;
      const rect = target.getBoundingClientRect();
      const x = e.clientX - rect.left - offsetX;
      const y = e.clientY - rect.top - offsetY;
      dispatch('positionupdate', { x, y });
    }

</script>

<div
  role="button"
  aria-label="Draggable node"
  tabindex="0"
  class="node-container absolute cursor-grab active:cursor-grabbing"
  class:selected
  style="left: {node.position.x}px; top: {node.position.y}px; z-index: {selected ? 100 : 1}"
  on:mousedown={handleDragStart}
  on:mousemove={handleDragMove}
>
<div
  class="connection-port input"
  role="button"
  aria-label="Input connection port"
  tabindex="0"
  on:mousedown={handleConnectionStart}
></div>
<div
  class="connection-port output"
  role="button"
  aria-label="Output connection port"
  tabindex="0"
  on:mousedown={handleConnectionEnd}
></div>

  <div class="node-header" style:background-color={NODE_TYPES[node.type].color}>
    <span class="icon">{NODE_TYPES[node.type].icon}</span>
    <span class="title">{node.data.title}</span>
  </div>
  <div
    class="node-content"
    role="button"
    aria-label="Draggable node content"
    tabindex="0"
    on:mousedown={handleDragStart}
  >
    {#if node.type === 'transport'}
      <div class="details">Transport Mode: {node.data.mode || 'Not specified'}</div>
    {:else if node.type === 'restaurant'}
      <div class="details">Cuisine: {node.data.cuisine || 'Any'}</div>
    {/if}
  </div>
</div>

<style>
  .node-container {
    width: 200px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.1s ease-out;
  }

  .node-header {
    padding: 12px;
    color: white;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .node-content {
    padding: 12px;
    background: white;
  }

  .selected {
    box-shadow: 0 0 0 2px #3B82F6;
  }

  .connection-port {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: #3B82F6;
      position: absolute;
      cursor: crosshair;
    }
    .connection-port.input { left: -6px; top: 50%; }
    .connection-port.output { right: -6px; top: 50%; }
</style>
