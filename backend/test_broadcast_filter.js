#!/usr/bin/env node
/**
 * Test Broadcast Type Filter
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_ANON_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

async function testFilters() {
  console.log('Testing Broadcast Type Filters\n');

  // Test 1: Get all broadcasts
  console.log('1. All broadcasts:');
  const { data: all, error: allError } = await supabase
    .from('broadcasts')
    .select('id, title, broadcast_type')
    .limit(5);

  if (allError) {
    console.error('Error:', allError);
  } else {
    all.forEach(b => console.log(`   ${b.id}: ${b.broadcast_type} - ${b.title.substring(0, 50)}`));
  }

  // Test 2: Filter by replays
  console.log('\n2. Filter by replays:');
  const { data: replays, error: replaysError } = await supabase
    .from('broadcasts')
    .select('id, title, broadcast_type')
    .eq('broadcast_type', 'replays')
    .limit(3);

  if (replaysError) {
    console.error('Error:', replaysError);
  } else {
    console.log(`   Found ${replays.length} replays`);
    replays.forEach(b => console.log(`   ${b.id}: ${b.broadcast_type} - ${b.title.substring(0, 50)}`));
  }

  // Test 3: Filter by lives
  console.log('\n3. Filter by lives:');
  const { data: lives, error: livesError } = await supabase
    .from('broadcasts')
    .select('id, title, broadcast_type')
    .eq('broadcast_type', 'lives')
    .limit(3);

  if (livesError) {
    console.error('Error:', livesError);
  } else {
    console.log(`   Found ${lives.length} lives`);
    lives.forEach(b => console.log(`   ${b.id}: ${b.broadcast_type} - ${b.title.substring(0, 50)}`));
  }

  // Test 4: Filter by shortclips
  console.log('\n4. Filter by shortclips:');
  const { data: shortclips, error: shortclipsError } = await supabase
    .from('broadcasts')
    .select('id, title, broadcast_type')
    .eq('broadcast_type', 'shortclips')
    .limit(3);

  if (shortclipsError) {
    console.error('Error:', shortclipsError);
  } else {
    console.log(`   Found ${shortclips.length} shortclips`);
    shortclips.forEach(b => console.log(`   ${b.id}: ${b.broadcast_type} - ${b.title.substring(0, 50)}`));
  }

  // Test 5: Check distribution
  console.log('\n5. Broadcast type distribution:');
  const { data: stats } = await supabase
    .from('broadcasts')
    .select('broadcast_type');

  const distribution = stats.reduce((acc, b) => {
    const type = b.broadcast_type || 'null';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  Object.entries(distribution).forEach(([type, count]) => {
    console.log(`   ${type}: ${count}`);
  });
}

testFilters().then(() => process.exit(0)).catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
