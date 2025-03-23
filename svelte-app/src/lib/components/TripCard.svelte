<script lang="ts">
  export let title: string;
  export let destination: string;
  export let startDate: Date;
  export let endDate: Date;
  export let status: 'not-started' | 'in-progress' | 'completed';
  export let imageUrl: string;

  const statusColors = {
    'not-started': 'bg-gray-200 text-[#292d2f]',
    'in-progress': 'bg-blue-100 text-blue-700',
    'completed': 'bg-[#84b37e] bg-opacity-20 text-[#84b37e]'
  };
</script>

<div class="bg-[var(--bg-primary)] rounded-lg shadow-md overflow-hidden transition-all duration-300 hover:shadow-lg">
  <img src={imageUrl} alt={destination} class="w-full h-48 object-cover" />
  <div class="p-4">
    <div class="flex justify-between items-start mb-2">
      <h3 class="text-lg font-normal text-[var(--text-primary)]">{title}</h3>
      <span class={`px-2 py-1 rounded-full text-xs font-light ${statusColors[status]}`}>
        {status}
      </span>
    </div>
    <p class="text-[var(--text-secondary)] mb-4 font-light">{destination}</p>
    <div class="text-sm text-[var(--text-secondary)] font-light">
      {startDate.toLocaleDateString()} - {endDate.toLocaleDateString()}
    </div>
    <div class="mt-4 flex gap-2">
      <button class="px-3 py-1 bg-[#84b37e] text-white rounded hover:bg-opacity-90 transition-colors duration-200 font-light text-sm">
        Edit
      </button>
      <button class="px-3 py-1 bg-[var(--bg-secondary)] text-[var(--text-secondary)] rounded hover:bg-opacity-90 transition-colors duration-200 font-light text-sm">
        Share
      </button>
    </div>
  </div>
</div>