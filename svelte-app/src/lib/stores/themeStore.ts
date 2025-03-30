// src/lib/stores/themeStore.ts
import { writable } from 'svelte/store';
import { browser } from '$app/environment';

const getInitialTheme = () => {
  if (browser) {
    return localStorage.getItem('theme') || 'dark';
  }
  return 'dark';
};

export const theme = writable(getInitialTheme());

if (browser) {
  theme.subscribe(value => {
    localStorage.setItem('theme', value);
  });
}