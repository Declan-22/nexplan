<script lang="ts">
  import { page } from '$app/stores';
  import { siloStore, updateNodePosition, addNode, getNodePosition, renameSilo, deleteSilo, createConnection, type Position } from '$lib/stores/siloStore';
  import Node from "$lib/components/Node.svelte";
  import NodeLibrary from '$lib/components/NodeLibrary.svelte';
  import { calculateConnectionPath } from '$lib/utils/nodeUtils';
  import type { SiloNode } from '$lib/stores/siloStore';
  import type { NodeType } from '$lib/types/nodes';
  import { goto } from '$app/navigation';


  let showLibrary = false;
  
  let activeNode: SiloNode | null = null;
  let renamingSilo = false;
  let newSiloName = 'My New Trip';
  let connectionStart: { nodeId: string, position: Position } | null = null;
  
  $: silo = $siloStore.find(s => s.id === $page.params.id);
  $: if (silo) newSiloName = silo.name;

  function createNewSilo() {
    const siloId = crypto.randomUUID();
    siloStore.update(store => [...store, {
      id: siloId,
      name: newSiloName,
      nodes: [],
      edges: []
    }]);
    goto(`/silos/${siloId}`);
  }
  function handleDelete(siloId: string, e: MouseEvent) {
    e.preventDefault();
    deleteSilo(siloId);
  }

  function handleAddNode(event: CustomEvent<NodeType>) {
    const type = event.detail;
    if (!silo) return;
    addNode(silo.id, type, { x: 100, y: 100 });
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
<div class="silos-page">
  <div class="header">
    <h1>Silos</h1>
    <button on:click={createNewSilo} class="create-button">
      + Create New Silo
    </button>
  </div>

  <div class="silos-grid">
    {#each $siloStore as silo}
      <a href="/silos/{silo.id}" class="silo-card" on:click|preventDefault={() => goto(`/silos/${silo.id}`)}>
        <div class="card-header">
          <h3>{silo.name}</h3>
          <button 
            on:click|stopPropagation={(e) => handleDelete(silo.id, e)}
            class="delete-button"
          >
            ×
          </button>
        </div>
        <p>{silo.nodes.length} nodes • {silo.edges.length} connections</p>
      </a>
    {/each}
  </div>
  <NodeLibrary show={showLibrary} on:add={handleAddNode} />
</div>

<div class="silo-editor">
  {#if silo}
    <div class="toolbar">
      {#if renamingSilo}
        <input
          bind:value={newSiloName}
          on:keydown={(e) => e.key === 'Enter' && renameSilo(silo.id, newSiloName) && (renamingSilo = false)}
          class="rename-input"
        />
      {:else}
        <h2>{silo.name}</h2>
        <button on:click={() => renamingSilo = true} class="toolbar-button">
          ✏️ Rename
        </button>
        <button on:click={() => deleteSilo(silo.id)} class="toolbar-button delete">
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

    <button
      on:click={() => showLibrary = true}
      class="add-button"
      aria-label="Add node"
    >
      +
    </button>
    


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
    color: white;
    border-radius: 4px;
    border: none;
    cursor: pointer;
  }

  .toolbar-button.delete {
    background: #ef4444;
  }

  .rename-input {
    padding: 0.5rem;
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
  }

  .add-button {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: var(--brand-green);
    color: white;
    font-size: 1.5rem;
    border: none;
    cursor: pointer;
    box-shadow: var(--shadow-md);
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
  .silo-card {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .silo-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  }
</style>
