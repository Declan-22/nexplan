<script lang="ts">
    import { supabase } from '$lib/supabaseClient';
    import { page } from '$app/stores';
    
    let email = '';
    let password = '';
    let error = '';
    let loading = false;
  
    async function handleLogin() {
      loading = true;
      error = '';
      try {
        const { error: authError } = await supabase.auth.signInWithPassword({
          email,
          password
        });
        
        if (authError) throw authError;
        
        window.location.href = $page.url.searchParams.get('returnUrl') || '/';
      } catch (e) {
        error = e instanceof Error ? e.message : 'An unknown error occurred';
      } finally {
        loading = false;
      }
    }
  </script>
  
  <div class="max-w-md mx-auto mt-20 p-6 bg-white rounded-lg shadow-md">
    <h1 class="text-3xl font-light mb-6 text-center">Login</h1>
    
    {#if error}
      <div class="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
    {/if}
    
    <form on:submit|preventDefault={handleLogin} class="space-y-4">
      <div>
        <label for="email" class="block text-sm font-medium mb-1">Email</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          class="w-full p-2 border rounded"
          required
        >
      </div>
      
      <div>
        <label for="password" class="block text-sm font-medium mb-1">Password</label>
        <input
          type="password"
          bind:value={password}
          class="w-full p-2 border rounded"
          required
        >
      </div>
      
      <button
        type="submit"
        class="w-full py-2 px-4 bg-[#84b37e] text-white rounded hover:bg-opacity-90"
        disabled={loading}
      >
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
    
    <div class="mt-4 text-center">
      <span class="text-sm">Need an account? </span>
      <a href="/signup" class="text-[#84b37e] underline">Sign up</a>
    </div>
  </div>