<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { sidebarCollapsed } from '$lib/stores/uiStore';

  const navItems = [
    { name: 'Home', href: '/', icon: 'home' },
    { name: 'Silos', href: '/silos', icon: 'nodes' }
  ];

  // Ensure all items have a 'name' property
  if (!navItems.every(item => item.name)) {
    throw new Error("Each navItem must have a 'name' property.");
  }
</script>

<aside class="fixed inset-y-0 z-20 bg-[var(--bg-secondary)] border-r border-[var(--border-color)] transition-all duration-300 h-screen"
        class:w-64={!$sidebarCollapsed}
        class:w-20={$sidebarCollapsed}
        style="top: 0;"
>
  <div class="flex flex-col h-full">
    <!-- Collapse Toggle -->
    <button
      on:click={() => sidebarCollapsed.update((c: boolean) => !c)}
      class="p-4 hover:bg-[var(--bg-primary)] transition-colors"
    >
      {#if $sidebarCollapsed}
        <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 5l7 7-7 7M5 5l7 7-7 7"/>
        </svg>
      {:else}
        <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7"/>
        </svg>
      {/if}
    </button>

    <!-- Navigation -->
    <nav class="flex-1 p-2 space-y-1">
      {#each navItems as item}
        <div class="relative group">
          <button
            on:click={() => goto(item.href)}
            class={`w-full flex items-center p-3 rounded-lg transition-colors
              ${$page.url.pathname === item.href 
                ? 'bg-[var(--brand-green)] text-white' 
                : 'hover:bg-[var(--bg-primary)] text-[var(--text-secondary)]'}`}
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {#if item.icon === 'home'}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
              {:else}
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h3m-3 4h3m-6 4h3m-3 4h3M6 7h3v4H6V7zm0 10v-4h3v4H6z"/>
              {/if}
            </svg>
            {#if !$sidebarCollapsed}
              <span class="ml-3">{item.name}</span>
            {/if}
          </button>
          
          {#if $sidebarCollapsed}
            <div class="absolute left-full top-1/2 -translate-y-1/2 ml-2 px-3 py-2 bg-[var(--bg-primary)] text-[var(--text-primary)] rounded-md shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200">
              {item.name}
            </div>
          {/if}
        </div>
      {/each}
    </nav>
  </div>
</aside>