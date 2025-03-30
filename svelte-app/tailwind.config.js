// tailwind.config.js
export default {
  content: [
    './src/**/*.{html,js,svelte,ts}',
  ],
  theme: {
    extend: {
      spacing: {
        'sidebar-collapsed': '5rem',
        'sidebar-expanded': '16rem'
      },
      transitionProperty: {
        'width': 'width',
        'position': 'left, top',
        'z-index': 'z-index'
      }
    }
  },
  plugins: [],
};
