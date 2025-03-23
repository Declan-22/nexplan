<script lang="ts">
    import type { ItineraryDay } from '$lib/types/types';
    
    export let day: ItineraryDay;
    export let expanded = false;
  </script>
  
  <div class="nexplan-card overflow-hidden mb-6">
      <!-- Header -->
      <div 
          class="p-4 bg-[var(--bg-secondary)] cursor-pointer flex justify-between items-center border-b border-[var(--border-color)]"
          on:click={() => expanded = !expanded}
      >
          <div>
              <h3 class="font-bold text-lg">
                  <span class="text-[var(--brand-green)]">Day {day.day_number}</span> - {day.date}
              </h3>
          </div>
          <svg 
            class="h-6 w-6 text-[var(--brand-green)] transition-transform duration-300" 
            style={expanded ? "transform: rotate(180deg)" : ""}
            xmlns="http://www.w3.org/2000/svg" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor"
          >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
      </div>
  
      <!-- Content -->
      {#if expanded}
      <div class="p-4 space-y-6 transition-all duration-300 ease-in-out">
          <!-- Morning -->
          {#if day.activities.morning?.length}
          <div class="fade-in">
              <h4 class="font-semibold mb-3 text-[var(--accent-yellow)] flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  Morning
              </h4>
              <ul class="list-disc pl-6 space-y-2 text-[var(--text-secondary)]">
                  {#each day.activities.morning as activity}
                  <li>{activity}</li>
                  {/each}
              </ul>
          </div>
          {/if}
  
          <!-- Afternoon -->
          {#if day.activities.afternoon?.length}
          <div class="fade-in" style="animation-delay: 0.1s">
              <h4 class="font-semibold mb-3 text-[var(--accent-blue)] flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                  </svg>
                  Afternoon
              </h4>
              <ul class="list-disc pl-6 space-y-2 text-[var(--text-secondary)]">
                  {#each day.activities.afternoon as activity}
                  <li>{activity}</li>
                  {/each}
              </ul>
          </div>
          {/if}
  
          <!-- Evening -->
          {#if day.activities.evening?.length}
          <div class="fade-in" style="animation-delay: 0.2s">
              <h4 class="font-semibold mb-3 text-[var(--accent-purple)] flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                  </svg>
                  Evening
              </h4>
              <ul class="list-disc pl-6 space-y-2 text-[var(--text-secondary)]">
                  {#each day.activities.evening as activity}
                  <li>{activity}</li>
                  {/each}
              </ul>
          </div>
          {/if}
  
          <!-- Estimated Cost -->
          {#if day.estimated_cost}
          <div class="mt-4 pt-4 border-t border-[var(--border-color)] fade-in" style="animation-delay: 0.3s">
              <p class="text-[var(--text-secondary)] flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 text-[var(--brand-green)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Estimated Cost: 
                  <span class="text-[var(--brand-green)] font-medium ml-1">{day.estimated_cost}</span>
              </p>
          </div>
          {/if}
      </div>
      {/if}
  </div>