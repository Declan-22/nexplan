<script lang="ts">
  import TravelForm from '$lib/components/TravelForm.svelte';
  import { theme } from '$lib/stores/themeStore';
  let destination = '';
  let startDate = '';
  let endDate = '';

  function toggleTheme() {
    theme.update(t => t === 'dark' ? 'light' : 'dark');
    document.documentElement.setAttribute('data-theme', $theme);
  }

  // Set initial theme
  $: if (typeof document !== 'undefined') {
    document.documentElement.setAttribute('data-theme', $theme);
  }
</script>

<main class="min-h-screen bg-[var(--bg-primary)] p-8 transition-colors duration-300">
  <button 
    class="theme-toggle" 
    on:click={toggleTheme}
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

  <div class="min-h-screen py-12">
    <div class="max-w-7xl mx-auto px-4">
      <div class="text-center mb-12 space-y-4">
        <h1 class="text-4xl font-semibold mb-2 flex items-center justify-center gap-2">
          <img src="/nexplanlogo.png" alt="NexPlan Logo" class="h-10 w-10 transition-all duration-300 theme-logo" />
          <span class="nexplan-logo flex items-center">
            <span class="nex">nex</span><span class="plan">plan</span>
          </span>
        </h1>
        <p class="text-[var(--text-secondary)] text-xl font-light">Your AI-Powered Trip Planning Assistant</p>
      </div>
      
      <div class="nexplan-card mb-8">
        <TravelForm />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 pt-6">
        <div class="nexplan-card fade-in" style="animation-delay: 0.2s">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-[var(--brand-green)] mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
          <h2 class="text-xl font-semibold text-[var(--brand-green)] mb-4">Smart Planning</h2>
          <p class="text-[var(--text-secondary)] font-light">AI-powered itinerary creation based on your preferences and travel style.</p>
        </div>
        
        <div class="nexplan-card fade-in" style="animation-delay: 0.3s">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-[var(--brand-green)] mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <h2 class="text-xl font-semibold text-[var(--brand-green)] mb-4">Local Insights</h2>
          <p class="text-[var(--text-secondary)] font-light">Get recommendations for hidden gems and authentic experiences.</p>
        </div>
        
        <div class="nexplan-card fade-in" style="animation-delay: 0.4s">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-[var(--brand-green)] mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <h2 class="text-xl font-semibold text-[var(--brand-green)] mb-4">Real-Time Updates</h2>
          <p class="text-[var(--text-secondary)] font-light">Stay informed with live updates and travel alerts during your trip.</p>
        </div>
      </div>
    </div>
  </div>
</main>