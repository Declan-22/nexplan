
<script lang="ts">
  import { onMount } from 'svelte';
  import { browser } from '$app/environment';
  import DayCard from './DayCard.svelte';
  import TravelTips from './TravelTips.svelte';
  import type { Itinerary } from '$lib/types/types';
  import { currentItinerary, updateItinerary } from '$lib/stores/itineraryStore';
  import { getSupabaseSession, isSessionValid } from '$lib/auth';

  export let itineraryId: string;
  export let itinerary: Itinerary | null = null;
  
  let modification = '';
  let loading = false;
  let error = '';
  let success = '';
  let expandedDays: number[] = [1];
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

  // Add this reactive variable
  let canUpdate = false;
  $: {
    isSessionValid().then(valid => {
      canUpdate = valid;
    });
  }
  
  // Modify your template to hide update form when not logged in

  onMount(async () => {
    if ($currentItinerary?.id === itineraryId) {
      itinerary = $currentItinerary;
      return;
    }
    
    loading = true;
    try {
      const VITE_API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      const response = await fetch(`${VITE_API_URL}/api/itinerary/${itineraryId}`);
      console.log(`Fetching from: ${VITE_API_URL}/api/itinerary/${itineraryId}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to load itinerary');
      }
      
      itinerary = await response.json();
      currentItinerary.set(itinerary);
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load itinerary';
      console.error('Fetch error:', e);
    } finally {
      loading = false;
    }
  });

  function handleSessionExpiration() {
    error = 'Your session has expired. Redirecting to login...';
    setTimeout(() => {
      window.location.href = '/login';
    }, 2000);
  }

  function toggleDayExpansion(dayNumber: number) {
    expandedDays = expandedDays.includes(dayNumber)
      ? expandedDays.filter(d => d !== dayNumber)
      : [...expandedDays, dayNumber];
  }

  async function handleModificationSubmit() {
    if (!isSessionValid()) {
      error = 'Please log in to modify itineraries';
      setTimeout(() => window.location.href = '/login', 2000);
      return;
    }

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
        setTimeout(() => success = '', 3000);
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Update failed';
      console.error('Update error:', e);
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
          <span class="font-normal">Travelers:</span> {itinerary.people || 'Not specified'}
        </div>
        <div class="bg-[var(--bg-primary)] p-3 rounded shadow">
          <span class="font-normal">Accommodation:</span> {itinerary.accommodation || 'Not specified'}
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
      
      {#if canUpdate}
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
      {:else}
        <div class="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          Please <a href="/login" class="underline">log in</a> to modify this itinerary
        </div>
      {/if}
    </div>
  {/if}
</div>
