import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';



export default {
	plugins: [tailwindcss(), sveltekit()],
	server: {
	  proxy: {
		'/api': {
		  target: 'http://localhost:5000', // your Flask backend port
		  changeOrigin: true,
		  secure: false
		}
	  }
	}
  };
