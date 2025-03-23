import adapter from '@sveltejs/adapter-static'; // Change this
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      // Output directory for your static build
      fallback: 'index.html'
    })
  }
};

export default config;

