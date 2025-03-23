<script lang="ts">
  export let tips: string[] = [];
</script>

<div class="bg-[var(--bg-primary)] rounded-lg shadow-md overflow-hidden">
  <div class="p-4 bg-[#84b37e] text-white">
    <h3 class="font-normal text-lg">Travel Tips</h3>
  </div>
  
  <div class="p-4">
    {#if tips.length > 0}
      <ul class="space-y-3">
        {#each tips as tip}
          <li class="flex items-start">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-[#84b37e] mr-2 mt-0.5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span class="font-light text-[var(--text-primary)]">{tip}</span>
          </li>
        {/each}
      </ul>
    {:else}
      <p class="text-[var(--text-secondary)] font-light">No travel tips available.</p>
    {/if}
  </div>
</div>