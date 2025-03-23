<script lang="ts">
    import { page } from '$app/stores';
    import ItineraryView from '$lib/components/ItineraryView.svelte';
    
    const itineraryId = $page.params.id;
  </script>
  
  <svelte:head>
    <title>Your Travel Itinerary | AI Travel Planner</title>
  </svelte:head>
  
  <div class="min-h-screen bg-blue-50 py-12">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex items-center mb-8">
        <a href="/" class="text-blue-600 hover:text-blue-800 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
          </svg>
          Back to Home
        </a>
      </div>
      
      <ItineraryView {itineraryId} />
    </div>
  </div>