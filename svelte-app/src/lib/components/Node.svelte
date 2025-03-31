<script lang="ts">
  import { createEventDispatcher, onMount, onDestroy } from 'svelte';
  import type { SiloNode } from '$lib/stores/siloStore';
  import { NODE_TYPES } from '$lib/types/nodes';
  import { snapToGrid } from '$lib/utils/nodeUtils';
  import { shouldHaveInputPort, shouldHaveOutputPort } from '$lib/stores/siloStore';

  export let node: SiloNode;
  export let selected = false;
  export let hasError = false;

  const dispatch = createEventDispatcher();
  let nodeElement: HTMLElement;
  let inputPort: HTMLElement | null = null;
  let outputPort: HTMLElement | null = null;
  
  let isDragging = false;
  let dragStartX = 0;
  let dragStartY = 0;
  let initialPosition = { x: node.position.x, y: node.position.y };
  
  // Use RAF to improve performance of dragging
  let animationFrameId: number | null = null;
  let pendingPositionUpdate: { x: number, y: number } | null = null;
  
  function schedulePositionUpdate(position: { x: number, y: number }) {
    pendingPositionUpdate = position;
    
    if (animationFrameId === null) {
      animationFrameId = requestAnimationFrame(() => {
        if (pendingPositionUpdate) {
          dispatch('positionupdate', pendingPositionUpdate);
          pendingPositionUpdate = null;
        }
        animationFrameId = null;
      });
    }
  }
  
  function handleMouseDown(e: MouseEvent) {
    // Only trigger on primary mouse button (left click)
    if (e.button !== 0) return;
    
    isDragging = true;
    dragStartX = e.clientX;
    dragStartY = e.clientY;
    initialPosition = { x: node.position.x, y: node.position.y };
    
    dispatch('dragstart', node);
    
    // Prevent text selection during drag
    e.preventDefault();
  }
  
  function handleMouseMove(e: MouseEvent) {
    if (!isDragging) return;
    
    const dx = e.clientX - dragStartX;
    const dy = e.clientY - dragStartY;
    
    const newPos = snapToGrid({
      x: initialPosition.x + dx,
      y: initialPosition.y + dy
    });
    
    schedulePositionUpdate(newPos);
  }
  
  function handleMouseUp() {
    if (isDragging) {
      isDragging = false;
    }
  }
  
  function getPortPosition(el: HTMLElement) {
    if (!el) return { x: 0, y: 0 };
    
    const rect = el.getBoundingClientRect();
    return {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2
    };
  }
  
  function handleConnectionStart(e: MouseEvent) {
    e.stopPropagation(); // Prevent node drag when connecting
    if (outputPort) {
      const position = getPortPosition(outputPort);
      dispatch('connectionstart', {
        nodeId: node.id,
        position
      });
    }
  }

  function handleConnectionEnd(e: MouseEvent) {
    e.stopPropagation(); // Prevent node drag when connecting
    if (inputPort) {
      const position = getPortPosition(inputPort);
      dispatch('connectionend', {
        nodeId: node.id,
        position
      });
    }
  }

  function handleRename(event: Event) {
    const target = event.target as HTMLInputElement;
    dispatch('rename', target.value);
  }

  function updatePortPositions() {
    // Define port positions object with safe defaults
    const positions = {
      input: { x: 0, y: 0 },
      output: { x: 0, y: 0 }
    };
    
    // Only update positions for ports that exist
    if (shouldHaveInputPort(node.type) && inputPort) {
      positions.input = getPortPosition(inputPort);
    }
    
    if (shouldHaveOutputPort(node.type) && outputPort) {
      positions.output = getPortPosition(outputPort);
    }
    
    dispatch('portupdate', positions);
  }

  onMount(() => {
    if (nodeElement) {
      nodeElement.addEventListener('mousedown', handleMouseDown);
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      
      // Add a small delay to ensure DOM is fully rendered
      setTimeout(updatePortPositions, 50);
      
      // Update port positions when position changes
      const resizeObserver = new ResizeObserver(() => {
        updatePortPositions();
      });
      resizeObserver.observe(nodeElement);
    }
  });

  onDestroy(() => {
    if (animationFrameId !== null) {
      cancelAnimationFrame(animationFrameId);
    }
    
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mouseup', handleMouseUp);
    
    if (nodeElement) {
      nodeElement.removeEventListener('mousedown', handleMouseDown);
    }
  });
</script>

<div
  bind:this={nodeElement}
  class="node-container"
  class:node-selected={selected}
  class:node-error={hasError}
  style="transform: translate({node.position.x}px, {node.position.y}px)"
>
  <!-- Node Header with Icon and Title -->
  <div class="node-header" style="background: linear-gradient(135deg, {NODE_TYPES[node.type].color}, {NODE_TYPES[node.type].color}CC)">
    <div class="node-icon">
      {@html NODE_TYPES[node.type].icon}
    </div>
    <input
      class="node-title"
      bind:value={node.data.title}
      on:change={handleRename}
      spellcheck="false"
    />
  </div>
  
  <!-- Node Content -->
  <div class="node-content">
    {#if node.type === 'transport'}
      <div class="input-group">
        <label class="input-label" for="transport-mode">Transport Mode</label>
        <select id="transport-mode" class="node-select">
          <option value="car">Car</option>
          <option value="train">Train</option>
          <option value="flight">Flight</option>
        </select>
      </div>
    {:else if node.type === 'restaurant'}
      <div class="input-group">
        <label class="input-label" for="cuisine-type">Cuisine Type</label>
        <input
          id="cuisine-type"
          type="text"
          class="node-input"
          placeholder="e.g., Italian, Japanese..."
        />
      </div>
    {/if}
  </div>
  
<!-- Connection Ports -->
{#if shouldHaveInputPort(node.type)}
  <div bind:this={inputPort} class="port port-input" on:mousedown={handleConnectionEnd} role="button" tabindex="0" aria-label="Input Port">
    <div class="port-dot"></div>
    <div class="port-label">Input</div>
  </div>
{/if}

{#if shouldHaveOutputPort(node.type)}
  <div bind:this={outputPort} class="port port-output" on:mousedown={handleConnectionStart} role="button" tabindex="0" aria-label="Output Port">
    <div class="port-label">Output</div>
    <div class="port-dot"></div>
  </div>
{/if}
</div>


<style>
  .node-container {
    position: relative;
    width: 280px;
    border-radius: 12px;
    background: white;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08), 0 1px 3px rgba(0, 0, 0, 0.05);
    overflow: visible;
    cursor: move;
    transition: transform 0.05s ease, box-shadow 0.2s ease;
    user-select: none;
    z-index: 10;
  }
  
  .node-container:hover {
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12), 0 2px 8px rgba(0, 0, 0, 0.06);
  }
  
  .node-selected {
    box-shadow: 0 0 0 2px #3B82F6, 0 8px 30px rgba(0, 0, 0, 0.12);
    z-index: 100;
  }
  
  .node-error {
    box-shadow: 0 0 0 2px rgb(239, 68, 68), 0 8px 30px rgba(239, 68, 68, 0.1);
    animation: pulse 2s infinite;
  }
  
  .node-header {
    display: flex;
    align-items: center;
    padding: 16px;
    border-radius: 12px 12px 0 0;
    color: white;
    gap: 12px;
  }
  
  .node-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 8px;
    padding: 8px;
  }
  
  .node-icon :global(svg) {
    width: 20px;
    height: 20px;
    color: white;
  }
  
  .node-title {
    flex: 1;
    background: transparent;
    border: none;
    color: white;
    font-size: 1rem;
    font-weight: 600;
    padding: 4px 0;
    border-bottom: 2px solid transparent;
  }
  
  .node-title:focus {
    outline: none;
    border-bottom: 2px solid rgba(255, 255, 255, 0.5);
  }
  
  .node-content {
    padding: 16px;
    background: white;
    border-radius: 0 0 12px 12px;
  }
  
  .input-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 8px;
  }
  
  .input-label {
    font-size: 0.75rem;
    color: #64748B;
    font-weight: 500;
  }
  
  .node-select,
  .node-input {
    width: 100%;
    padding: 8px 12px;
    border-radius: 6px;
    border: 1px solid #E2E8F0;
    background: #F8FAFC;
    font-size: 0.875rem;
    transition: all 0.2s ease;
  }
  
  .node-select:focus,
  .node-input:focus {
    outline: none;
    border-color: #3B82F6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }
  
  /* Port styling */
  .port {
    position: absolute;
    top: 50%;
    display: flex;
    align-items: center;
    cursor: crosshair;
    z-index: 20;
  }
  
  .port-input {
    left: -14px;
    transform: translateY(-50%);
    flex-direction: row;
  }
  
  .port-output {
    right: -14px;
    transform: translateY(-50%);
    flex-direction: row-reverse;
  }
  
  .port-dot {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: #3B82F6;
    border: 2px solid white;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    z-index: 30;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  
  .port-label {
    font-size: 0.7rem;
    color: #64748B;
    font-weight: 500;
    opacity: 0;
    transition: opacity 0.2s ease, transform 0.2s ease;
    position: absolute;
    white-space: nowrap;
  }
  
  .port-input .port-label {
    left: 20px;
    transform: translateX(-5px);
  }
  
  .port-output .port-label {
    right: 20px;
    transform: translateX(5px);
  }
  
  .port:hover .port-dot {
    transform: scale(1.2);
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  }
  
  .port:hover .port-label {
    opacity: 1;
    transform: translateX(0);
  }
  
  @keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4), 0 8px 30px rgba(239, 68, 68, 0.1); }
    70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0), 0 8px 30px rgba(239, 68, 68, 0.1); }
    100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0), 0 8px 30px rgba(239, 68, 68, 0.1); }
  }
  
  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .node-container {
      background: #1E293B;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2), 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .node-content {
      background: #1E293B;
    }
    
    .node-select,
    .node-input {
      border-color: #334155;
      background: #0F172A;
      color: #E2E8F0;
    }
    
    .input-label {
      color: #94A3B8;
    }
    
    .port-label {
      color: #94A3B8;
    }
    
    .port-dot {
      border-color: #1E293B;
    }
  }
</style>