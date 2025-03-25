<script lang="ts">
    import { supabase } from '$lib/supabaseClient';
    
    let email = '';
    let password = '';
    let error = '';
    let loading = false;
    let success = false;
  
    async function handleSignup() {
      loading = true;
      error = '';
      try {
        const { error: authError } = await supabase.auth.signUp({
          email,
          password
        });
        
        if (authError) throw authError;
        success = true;
      } catch (e) {
        error = e instanceof Error ? e.message : 'An unknown error occurred';
      } finally {
        // Ensure no undeclared variables like 'r' are used here
        loading = false;
      }
    }
  </script>
  
  <div class="max-w-md mx-auto mt-20 p-6 bg-white rounded-lg shadow-md">
    <h1 class="text-3xl font-light mb-6 text-center">Sign Up</h1>
    
    {#if error}
      <div class="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
    {/if}
    
    {#if success}
      <div class="mb-4 p-3 bg-green-100 text-green-700 rounded">
        Check your email to confirm your account!
      </div>
    {:else}
      <form on:submit|preventDefault={handleSignup} class="space-y-4">
        <div>
          <label for="password">Email</label>
          <input id="email"
            type="email"
            bind:value={email}
            class="w-full p-2 border rounded"
            required
          >
        </div>
        
        <div>
          <label for="password">Password</label>
          <input id="password"
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
          {loading ? 'Creating account...' : 'Sign Up'}
        </button>
      </form>
    {/if}
  </div>