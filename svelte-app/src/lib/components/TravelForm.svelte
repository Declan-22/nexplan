<script lang="ts">
  import { onMount } from 'svelte';
  import { userInfo, createItinerary } from '$lib/stores/itineraryStore';
  import { goto } from '$app/navigation';
  
  let loading = false;
  let error = '';
  
  // Format the current date as YYYY-MM-DD for the date input default
  const today = new Date();
  const formattedDate = today.toISOString().split('T')[0];
  
  // Set default values
  onMount(() => {
    $userInfo.arrival_date = formattedDate;
    $userInfo.duration = '3';
    $userInfo.people = '1';
  });
  
  async function handleSubmit() {
    loading = true;
    error = '';
    
    try {
      // Validate input
      if (!$userInfo.destination) {
        throw new Error('Destination is required');
      }
      
      if (!$userInfo.budget) {
        throw new Error('Budget is required');
      }
      
      // Create the itinerary
      const itineraryId = await createItinerary($userInfo);
      
      if (itineraryId) {
        goto(`/itinerary/${itineraryId}`);
      } else {
        throw new Error('Failed to create itinerary');
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'An error occurred';
    } finally {
      loading = false;
    }
  }
</script>

<div class="max-w-2xl mx-auto">
<h2 class="text-2xl font-bold mb-6 text-center">Plan Your Perfect Trip</h2>

{#if error}
  <div class="bg-[var(--error)] bg-opacity-10 border border-[var(--error)] text-[var(--error)] px-4 py-3 rounded-lg mb-4">
    <div class="flex items-center">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      {error}
    </div>
  </div>
{/if}

<form on:submit|preventDefault={handleSubmit} class="space-y-6">
  <div>
    <label for="destination" class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
      Where are you planning to go?
    </label>
    <input
      type="text"
      id="destination"
      bind:value={$userInfo.destination}
      class="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] text-[var(--text-primary)]"
      placeholder="Paris, Tokyo, New York..."
      required
    />
  </div>
  
  <div>
    <label for="budget" class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
      What is your budget range for the trip?
    </label>
    <select
      id="budget"
      bind:value={$userInfo.budget}
      class="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] text-[var(--text-primary)]"
      required
    >
      <option value="">Select budget range</option>
      <option value="Budget ($0-$1000)">Budget ($0-$1000)</option>
      <option value="Moderate ($1000-$3000)">Moderate ($1000-$3000)</option>
      <option value="Luxury ($3000+)">Luxury ($3000+)</option>
    </select>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div>
      <label for="arrival_date" class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
        When will you be arriving?
      </label>
      <input
        type="date"
        id="arrival_date"
        bind:value={$userInfo.arrival_date}
        class="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] text-[var(--text-primary)]"
        required
      />
    </div>
    
    <div>
      <label for="duration" class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
        How many days will you be staying?
      </label>
      <input
        type="number"
        id="duration"
        bind:value={$userInfo.duration}
        min="1"
        max="30"
        class="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] text-[var(--text-primary)]"
        required
      />
    </div>
  </div>
  
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    <div>
      <label for="shelter" class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
        Where would you like to stay?
      </label>
      <select
        id="shelter"
        bind:value={$userInfo.shelter}
        class="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] text-[var(--text-primary)]"
        required
      >
        <option value="">Select accommodation</option>
        <option value="Hotel">Hotel</option>
        <option value="Airbnb">Airbnb</option>
        <option value="Hostel">Hostel</option>
        <option value="Resort">Resort</option>
        <option value="Apartment">Apartment</option>
      </select>
    </div>
    
    <div>
      <label for="people" class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
        How many people are traveling?
      </label>
      <input
        type="number"
        id="people"
        bind:value={$userInfo.people}
        min="1"
        max="20"
        class="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] text-[var(--text-primary)]"
        required
      />
    </div>
  </div>
  
  <div>
    <label for="activities" class="block text-sm font-medium text-[var(--text-secondary)] mb-1">
      What activities are you interested in?
    </label>
    <textarea
      id="activities"
      bind:value={$userInfo.activities}
      rows="3"
      class="w-full px-3 py-2 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-lg focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] text-[var(--text-primary)]"
      placeholder="Sightseeing, museums, hiking, beaches, local cuisine..."
      required
    ></textarea>
    <p class="text-xs text-[var(--text-secondary)] mt-1">Separate activities with commas</p>
  </div>
  
  <button
    type="submit"
    class="w-full py-3 px-4 bg-[var(--brand-green)] text-white font-medium rounded-lg hover:bg-[var(--brand-green-dark)] focus:outline-none focus:ring-2 focus:ring-[var(--brand-green)] focus:ring-offset-2 transition-all duration-300"
    disabled={loading}
  >
    {#if loading}
      <span class="flex items-center justify-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Creating Your Itinerary...
      </span>
    {:else}
      Plan My Trip
    {/if}
  </button>
</form>
</div>