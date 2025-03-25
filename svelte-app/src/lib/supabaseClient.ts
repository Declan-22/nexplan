// src/lib/supabaseClient.ts
import { createClient } from '@supabase/supabase-js'

// Add type safety
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error(`
    Missing Supabase credentials!
    Add VITE_SUPABASE_URL and VITE_SUPABASE_KEY
    to your .env file
  `);
}

export const supabase = createClient(supabaseUrl, supabaseKey);