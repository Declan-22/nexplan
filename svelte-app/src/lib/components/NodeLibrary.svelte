<script lang="ts">
    import { NODE_TYPES, type NodeType } from '$lib/types/nodes';
    import { createEventDispatcher } from 'svelte';
  
    export let show = false;
    const dispatch = createEventDispatcher<{ add: NodeType }>();
    function handleAdd(type: NodeType) {
    dispatch('add', type);
  }
  </script>
  
  {#if show}
    <div class="node-library">
      {#each Object.entries(NODE_TYPES) as [type, style]}
        <button
          class="node-option"
          on:click={() => dispatch('add', type as NodeType)}
        >
          <span class="icon">{style.icon}</span>
          <span class="label">{type}</span>
        </button>
      {/each}
    </div>
  {/if}
  
  <style>
    .node-library {
      position: fixed;
      top: 100px;
      right: 20px;
      background: white;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.15);
      padding: 12px;
      width: 200px;
      z-index: 1000;
    }
  
    .node-option {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px;
      width: 100%;
      border: none;
      background: none;
      cursor: pointer;
    }
  </style>