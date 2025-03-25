// src/lib/auth.ts
import { supabase } from './supabaseClient';
import { browser } from '$app/environment';

export async function getSupabaseSession() {
  if (!browser) return null;
  const { data } = await supabase.auth.getSession();
  return data.session;
}

export async function isSessionValid() {
  if (!browser) return false;
  const { data } = await supabase.auth.getSession();
  const session = data.session;
  return session !== null && Date.now() < (session.expires_at ?? 0) * 1000;
}