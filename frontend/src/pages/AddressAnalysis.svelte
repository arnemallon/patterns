<script>
  import { fly } from 'svelte/transition';
  import { useLocation } from 'svelte-routing';
  import AddressClassifier from '../components/AddressClassifier.svelte';

  let addressToClassify = '';

  const location = useLocation();

  // Keep the address in sync with the URL (works for both full page loads
  // and client-side navigation, e.g. from the history or dashboard)
  $: if ($location.pathname === '/analysis') {
    // The router's initial location has no `search`, so fall back to the
    // browser location on the first load
    const search = $location.search ?? window.location.search;
    const addressParam = new URLSearchParams(search).get('address');
    if (addressParam && addressParam !== addressToClassify) {
      addressToClassify = addressParam;
    }
  }
</script>

<div class="address-analysis" in:fly={{ y: 20, duration: 500 }}>
  <AddressClassifier bind:address={addressToClassify} />
</div>

<style>
  .address-analysis {
    max-width: 900px;
    margin: 0 auto;
    padding-top: var(--spacing-xl);
    font-family: var(--font-family);
    font-weight: var(--font-weight-normal);
    color: var(--text-primary);
  }
</style>
