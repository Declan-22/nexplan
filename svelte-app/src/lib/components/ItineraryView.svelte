<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import DayCard from './DayCard.svelte';
  import TravelTips from './TravelTips.svelte';
  import type { Itinerary } from '$lib/types/types';
  import { currentItinerary, updateItinerary } from '$lib/stores/itineraryStore';
  
  export let itineraryId: string;
  export let itinerary: Itinerary | null = null;
  
  let modification = '';
  let loading = false;
  let error = '';
  let success = '';
  let expandedDays: number[] = [1]; // Start with the first day expanded
  let totalCost = 0;
  let parsedBudget = 0;
  let accommodations = [];
  let restaurants = [];
  
  $: formattedDays = itinerary?.days?.map(day => ({
    ...day,
    activities: {
      morning: day.activities?.morning || ['Morning activities being planned...'],
      afternoon: day.activities?.afternoon || ['Afternoon activities being planned...'],
      evening: day.activities?.evening || ['Evening activities being planned...']
    }
  })) || [];
  
  onMount(async () => {
    if ($currentItinerary && $currentItinerary.id === itineraryId) {
      itinerary = $currentItinerary;
    } else {
      loading = true;
      try {
        const response = await fetch(`/api/itinerary/${itineraryId}`);
        if (response.ok) {
          itinerary = await response.json();
          currentItinerary.set(itinerary);
        } else {
          error = 'Failed to load itinerary';
        }
      } catch (e) {
        error = 'An error occurred while loading the itinerary';
        console.error(e);
      } finally {
        loading = false;
      }
    }
  });
  
  function toggleDayExpansion(dayNumber: number) {
    if (expandedDays.includes(dayNumber)) {
      expandedDays = expandedDays.filter(d => d !== dayNumber);
    } else {
      expandedDays = [...expandedDays, dayNumber];
    }
  }
  
  async function handleModificationSubmit() {
    if (!modification.trim()) {
      error = 'Please enter your modification request';
      return;
    }
    
    loading = true;
    error = '';
    success = '';
    
    try {
      const updatedItinerary = await updateItinerary(itineraryId, modification);
      if (updatedItinerary) {
        itinerary = updatedItinerary;
        success = 'Itinerary updated successfully!';
        modification = '';
      } else {
        throw new Error('Failed to update itinerary');
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'An error occurred while updating';
    } finally {
      loading = false;
    }
  }
</script>

<div class="max-w-4xl mx-auto p-4">
{#if loading && !itinerary}
  <div class="flex justify-center items-center min-h-32">
    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#84b37e]"></div>
  </div>
{:else if error && !itinerary}
  <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
    {error}
  </div>
{:else if itinerary}
  <div class="bg-[var(--bg-secondary)] rounded-lg shadow-lg p-6 mb-8">
    <h1 class="text-3xl font-normal text-center mb-2 text-[var(--text-primary)]">{itinerary.destination}</h1>
    {#if itinerary.country}
      <h2 class="text-xl text-center text-[var(--text-secondary)] mb-4 font-light">{itinerary.country}</h2>
    {/if}
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      <div class="bg-[var(--bg-primary)] p-3 rounded shadow">
        <span class="font-normal">Travel Dates:</span> {itinerary.arrival_date} for {itinerary.duration} days
      </div>
      <div class="bg-[var(--bg-primary)] p-3 rounded shadow">
        <span class="font-normal">Budget:</span> {itinerary.budget}
      </div>
      <div class="bg-[var(--bg-primary)] p-3 rounded shadow">
        <span class="font-normal">Travelers:</span> {itinerary.people}
      </div>
      <div class="bg-[var(--bg-primary)] p-3 rounded shadow">
        <span class="font-normal">Accommodation:</span> {itinerary.accommodation}
      </div>
    </div>
    
    <div class="mb-8">
      <h3 class="text-2xl font-normal mb-4 text-[var(--text-primary)]">Your Day-by-Day Itinerary</h3>
      {#each itinerary.days as day, index (day.day_number ?? index)}
        <DayCard {day} expanded={expandedDays.includes(day.day_number ?? index)} />
      {/each}
    </div>
    
    <div class="mb-8">
      <TravelTips tips={itinerary.travel_tips} />
    </div>
    
    <div class="bg-[var(--bg-primary)] rounded-lg shadow-md p-6">
      <h3 class="text-xl font-normal mb-4 text-[var(--text-primary)]">Need Changes?</h3>
      
      {#if error}
        <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      {/if}
      
      {#if success}
        <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {success}
        </div>
      {/if}
      
      <form on:submit|preventDefault={handleModificationSubmit} class="space-y-4">
        <div>
          <label for="modification" class="block text-sm font-light text-[var(--text-secondary)] mb-1">
            Tell us what you'd like to modify:
          </label>
          <textarea
            id="modification"
            bind:value={modification}
            rows="4"
            class="w-full px-3 py-2 border border-[var(--border-color)] rounded-md focus:outline-none focus:ring-2 focus:ring-[#84b37e] bg-[var(--bg-primary)] text-[var(--text-primary)]"
            placeholder="e.g., Add more museum visits, change day 2 to focus on outdoor activities, include more budget-friendly options..."
          ></textarea>
        </div>
        
        <button
          type="submit"
          class="py-2 px-4 bg-[#84b37e] text-white font-light rounded-md hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-[#84b37e] focus:ring-offset-2 transition-colors duration-200"
          disabled={loading}
        >
          {loading ? 'Updating...' : 'Update Itinerary'}
        </button>
      </form>
    </div>
  </div>
{:else}
  <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
    No itinerary found. <a href="/" class="underline">Create a new one</a>.
  </div>
{/if}
</div>