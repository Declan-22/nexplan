<script lang="ts">
	import '../app.css';
	let { children } = $props();
	import Sidebar from '$lib/components/Sidebar.svelte';
	import { theme } from '$lib/stores/themeStore';

  	import { browser } from '$app/environment';
  	import { onMount } from 'svelte';

  if (browser) {
    onMount(() => {
      const savedTheme = localStorage.getItem('theme') || 'dark';
      theme.set(savedTheme);
      
      return theme.subscribe(t => {
        document.documentElement.setAttribute('data-theme', t);
        localStorage.setItem('theme', t);
      });
    });
  }

  function toggleTheme() {
    theme.update(t => t === 'dark' ? 'light' : 'dark');
  }
</script>

<div class="flex min-h-screen">
	<Sidebar />
	
	<main class="flex-1 bg-[var(--bg-primary)] transition-colors duration-300 ml-20 lg:ml-64">
	  <!-- Original Theme Toggle -->
	  <button 
	  class="theme-toggle fixed top-4 right-4 z-50"
	  onclick={toggleTheme}
	  aria-label="Toggle theme"
	>
	  {#if $theme === 'dark'}
		<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
		  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
		</svg>
	  {:else}
		<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
		  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
		</svg>
	  {/if}
	  </button>
	  
	  {@render children()}
	  <div data-theme={$theme}>
	</main>
  </div>