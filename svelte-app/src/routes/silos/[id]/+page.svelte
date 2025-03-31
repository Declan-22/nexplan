<script lang="ts">
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { siloStore, updateNodePosition, addNode, getNodePosition, renameSilo, deleteSilo, createConnection, type Position } from '$lib/stores/siloStore';
    import Node from "$lib/components/Node.svelte";
    import NodeLibrary from '$lib/components/NodeLibrary.svelte';
    import { calculateConnectionPath } from '$lib/utils/nodeUtils';
    import type { SiloNode } from '$lib/stores/siloStore';
    import type { NodeType } from '$lib/types/nodes';
  
    let showLibrary = false;
    let activeNode: SiloNode | null = null;
    let renamingSilo = false;
    let newSiloName = '';
    let connectionStart: { nodeId: string, position: Position } | null = null;
  
    $: silo = $siloStore.find(s => s.id === $page.params.id);
    $: if (silo) newSiloName = silo.name;
  
    function handleAddNode(event: CustomEvent<NodeType>) {
      if (!silo) return;
      addNode(silo.id, event.detail, { x: 100, y: 100 });
      showLibrary = false;
    }
  
    function handleConnectionStart(event: CustomEvent<{ nodeId: string, position: Position }>) {
      connectionStart = event.detail;
    }
  
    function handleConnectionEnd(event: CustomEvent<{ nodeId: string, position: Position }>) {
      if (connectionStart && silo) {
        createConnection(connectionStart.nodeId, event.detail.nodeId, silo.id);
        connectionStart = null;
      }
    }
  </script>
  
  <div class="silo-editor">
    {#if silo}
      <div class="toolbar">
        {#if renamingSilo}
          <input
            bind:value={newSiloName}
            on:keydown={(e) => {
              if (e.key === 'Enter') {
                renameSilo(silo.id, newSiloName);
                renamingSilo = false;
              }
            }}
            class="rename-input"
          />
        {:else}
          <h2>{silo.name}</h2>
          <button on:click={() => renamingSilo = true} class="toolbar-button">
            ✏️ Rename
          </button>
          <button 
            on:click={() => {
              deleteSilo(silo.id);
              goto('/silos');
            }} 
            class="toolbar-button delete"
          >
            🗑️ Delete Silo
          </button>
        {/if}
      </div>
  
      <svg class="connections-layer">
        {#each silo.edges as edge}
          <path
            d={calculateConnectionPath(
              getNodePosition(silo.id, edge.source) ?? { x: 0, y: 0 },
              getNodePosition(silo.id, edge.target) ?? { x: 0, y: 0 }
            )}
            class="connection-line"
          />
        {/each}
      </svg>
  
      {#each silo.nodes as node (node.id)}
        <Node 
          {node} 
          on:dragstart={() => activeNode = node}
          on:positionupdate={({ detail }: { detail: Position }) => updateNodePosition(silo.id, node.id, detail)}
          on:connectionstart={handleConnectionStart}
          on:connectionend={handleConnectionEnd}
        />
      {/each}
  
      {#if silo.nodes.length === 0}
        <div class="empty-state">
          Click the + button to add your first node
        </div>
      {/if}
  
      <button
        on:click={() => showLibrary = true}
        class="add-button"
        aria-label="Add node"
      >
        +
      </button>
  
      <NodeLibrary show={showLibrary} on:add={handleAddNode} />
  
    {:else}
      <div class="error-message">
        Silo not found!
      </div>
    {/if}
  </div>
  
  <style>
    .silo-editor {
      position: relative;
      height: 100vh;
      background: var(--bg-primary);
    }
  
    .toolbar {
      padding: 1rem;
      background: var(--bg-secondary);
      display: flex;
      gap: 1rem;
      align-items: center;
      border-bottom: 1px solid var(--border-color);
    }
  
    .toolbar-button {
      padding: 0.5rem 1rem;
      background: var(--brand-green);
      color: var(--text-primary);
      border-radius: 4px;
      border: none;
      cursor: pointer;
      transition: opacity 0.2s ease;
    }
  
    .toolbar-button:hover {
      opacity: 0.9;
    }
  
    .toolbar-button.delete {
      background: var(--error);
    }
  
    .rename-input {
      padding: 0.5rem;
      background: var(--bg-primary);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      border-radius: 4px;
    }
  
    .add-button {
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      width: 3rem;
      height: 3rem;
      border-radius: 50%;
      background: var(--brand-green);
      color: var(--text-primary);
      font-size: 1.5rem;
      border: none;
      cursor: pointer;
      box-shadow: var(--shadow-md);
      z-index: 1000;
    }
  
    .connections-layer {
      position: absolute;
      width: 100%;
      height: 100%;
      pointer-events: none;
    }
  
    .connection-line {
      stroke: var(--brand-green);
      stroke-width: 2;
      fill: none;
    }
  
    .error-message {
      padding: 2rem;
      text-align: center;
      color: var(--text-primary);
    }
  
    .empty-state {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      color: var(--text-secondary);
      font-style: italic;
    }
  </style>
  