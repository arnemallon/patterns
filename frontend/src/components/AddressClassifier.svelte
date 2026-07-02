<script>
  import { createEventDispatcher } from 'svelte';
  import { navigate } from 'svelte-routing';
  import { apiService } from '../services/api.js';
  import { fly, scale } from 'svelte/transition';
  import TransactionGraph from './TransactionGraph.svelte';

  export let address = '';

  let inputValue = '';
  let result = null;
  let loading = false;
  let error = null;
  let showGraph = false;
  let lastClassifiedAddress = null;

  // Tracks the last value of the `address` prop so we can react ONLY when it
  // changes from the outside (URL parameter, history click, graph node click)
  // instead of on every keystroke - the latter would wipe what the user types.
  // Initialized to empty so the reactive block fires on mount when the component
  // is created with a pre-filled address (e.g. from URL or history navigation).
  let syncedAddress = '';

  const dispatch = createEventDispatcher();

  $: if (address !== syncedAddress) {
    syncedAddress = address;
    inputValue = address;
    if (address && address.trim() && address.trim() !== lastClassifiedAddress) {
      classify(address.trim());
    }
  }

  const featureLabels = {
    // Structural model (top-8 selected BABD-13 features)
    'S5': 'Avg. Shortest Path Length',
    'S6': 'Max. Graph Diameter',
    'S1-1': 'Avg. In-Degree',
    'PAIa13': 'Sent/Received Ratio',
    'PTIa21': 'Lifecycle / Active Days',
    'PTIa41-2': 'Min. Tx Interval (days)',
    'CI2a32-2': 'Max. Inflow Rate (BTC/day)',
    'CI3a12-3': 'Min. Daily In-Degree',
    // Non-structural model
    'S2-1': 'Max. In-Degree (Subgraph)',
    'S4': 'Betweenness Centrality',
    'PTIa41-3': 'Avg. Tx Interval (days)',
    // Legacy feature names (older history entries)
    'PAIa11-1': 'Total Received',
    'PAIa11-2': 'Total Sent',
    'S2-2': 'Max. Out-Degree (Subgraph)',
    'S2-3': 'Max. Total Degree (Subgraph)',
    'CI2a32-4': 'Max. Outflow Rate (BTC/day)'
  };

  const integerFeatures = ['S2-1', 'S2-2', 'S2-3', 'S6', 'CI3a12-3'];

  function goToAddress(addr) {
    const trimmed = (addr || '').trim();
    if (!trimmed) return;
    // Keep the URL in sync so the analysis is shareable / bookmarkable and the
    // address prop stays consistent with the router (single source of truth).
    navigate(`/analysis?address=${encodeURIComponent(trimmed)}`);
    syncedAddress = trimmed;
    inputValue = trimmed;
    if (trimmed !== lastClassifiedAddress) {
      classify(trimmed);
    }
  }

  function handleSubmit() {
    const trimmed = inputValue.trim();
    if (!trimmed) {
      error = { message: 'Validation Error', details: 'Please enter a Bitcoin address.' };
      return;
    }
    goToAddress(trimmed);
  }

  function handlePaste(e) {
    const pasted = (e.clipboardData || window.clipboardData)?.getData('text')?.trim();
    if (pasted) {
      setTimeout(() => goToAddress(pasted), 0);
    }
  }

  async function classify(addr) {
    loading = true;
    error = null;
    result = null;
    lastClassifiedAddress = addr;

    try {
      result = await apiService.classifyAddress(addr);
      dispatch('classificationComplete', result);
    } catch (err) {
      console.error('Caught error in component:', err);
      error = err;
    } finally {
      loading = false;
    }
  }

  function getCategoryDescription(prediction) {
    const categories = [
      'Blackmail', 'Cyber-security Service', 'Darknet Market', 'Centralized Exchange',
      'P2P Financial Infrastructure Service', 'P2P Financial Service', 'Gambling',
      'Government Criminal Blacklist', 'Money Laundering', 'Ponzi Scheme',
      'Mining Pool', 'Tumbler', 'Individual Wallet'
    ];

    const index = Math.round(prediction);
    const clampedIndex = Math.max(0, Math.min(12, index));
    return categories[clampedIndex];
  }

  function getCategoryInfo(prediction) {
    const category = getCategoryDescription(prediction);
    const categoryMap = {
      'Blackmail': { icon: '💀', color: '#dc3545' },
      'Cyber-security Service': { icon: '🛡️', color: '#17a2b8' },
      'Darknet Market': { icon: '🎭', color: '#343a40' },
      'Centralized Exchange': { icon: '🏦', color: '#007bff' },
      'P2P Financial Infrastructure Service': { icon: '🤝', color: '#fd7e14' },
      'P2P Financial Service': { icon: '💸', color: '#ffc107' },
      'Gambling': { icon: '🎲', color: '#28a745' },
      'Government Criminal Blacklist': { icon: '⚖️', color: '#6f42c1' },
      'Money Laundering': { icon: '🧼', color: '#e83e8c' },
      'Ponzi Scheme': { icon: '🔺', color: '#6610f2' },
      'Mining Pool': { icon: '⛏️', color: '#20c997' },
      'Tumbler': { icon: '🌀', color: '#343a40' },
      'Individual Wallet': { icon: '👤', color: '#6c757d' },
    };
    return categoryMap[category] || { icon: '❓', color: '#6c757d' };
  }

  $: categoryInfo = result ? getCategoryInfo(result.classification) : null;
  $: confidenceColor = result ? (result.confidence > 0.75 ? '#28a745' : result.confidence > 0.5 ? '#ffc107' : '#dc3545') : '#e9ecef';
  $: usedStructuralModel = result?.features && ('S5' in result.features) && ('S1-1' in result.features);
  const radius = 16;
  const circumference = 2 * Math.PI * radius;
  $: dashOffset = result ? circumference * (1 - result.confidence) : circumference;
</script>

<div class="classifier-container">
  <form class="search-form" on:submit|preventDefault={handleSubmit} in:fly={{ y: 20, duration: 300 }}>
    <div class="search-bar" class:loading>
      <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input
        type="text"
        bind:value={inputValue}
        on:paste={handlePaste}
        placeholder="Search a Bitcoin address..."
        spellcheck="false"
        autocomplete="off"
        disabled={loading}
      />
      {#if loading}
        <div class="search-spinner" aria-label="Analyzing..."></div>
      {:else}
        <button type="submit" class="search-submit" aria-label="Analyze address">
          Analyze
        </button>
      {/if}
    </div>
  </form>

  {#if error}
    <div class="error-display" in:fly|local={{ y: 20, duration: 300 }} out:fly|local={{ y: -20, duration: 200 }}>
      <strong>{error.message}</strong>
      {#if error.details}<p>{error.details}</p>{/if}
    </div>
  {/if}

  {#if loading}
    <div class="loading-skeleton" in:fly={{ y: 20, duration: 300 }}>
      <div class="skeleton-body">
        <div class="skeleton-row">
          <div class="skeleton-circle"></div>
          <div class="skeleton-lines">
            <div class="skeleton-line short"></div>
            <div class="skeleton-line"></div>
          </div>
          <div class="skeleton-gauge"></div>
        </div>
      </div>
      <div class="skeleton-features">
        {#each Array(8) as _}
          <div class="skeleton-feature-item">
            <div class="skeleton-line short"></div>
            <div class="skeleton-line"></div>
          </div>
        {/each}
      </div>
    </div>
  {/if}

  {#if result}
    <div class="result-card" in:scale|local={{ duration: 300, start: 0.95 }} out:scale|local={{ duration: 150 }}>
      <div class="result-main">
        <div class="category-display">
          {#if categoryInfo}
            <div class="category-icon" style="background-color: {categoryInfo.color};">
              <span class="icon">{categoryInfo.icon}</span>
            </div>
          {/if}
          <div class="category-text">
            <span class="label">Classification Result</span>
            <h2>{getCategoryDescription(result.classification)}</h2>
            <span class="model-badge">
              {usedStructuralModel ? 'Structural model (transaction graph)' : 'Non-structural model (API features)'}
            </span>
          </div>
        </div>
        <div class="result-side">
          <div class="confidence-gauge">
            <svg class="gauge-svg" viewBox="0 0 36 36">
              <circle
                class="gauge-base"
                cx="18"
                cy="18"
                r={radius}
                fill="none"
                stroke-width="3.8"
              />
              <circle
                class="gauge-arc"
                cx="18"
                cy="18"
                r={radius}
                fill="none"
                stroke="{confidenceColor}"
                stroke-width="3.8"
                stroke-dasharray="{circumference}"
                stroke-dashoffset="{dashOffset}"
                stroke-linecap="round"
                style="transition: stroke-dashoffset 0.5s;"
                transform="rotate(-90 18 18)"
              />
            </svg>
            <div class="gauge-text">
              {(result.confidence * 100).toFixed(0)}<span>%</span>
            </div>
          </div>
          <span class="gauge-label">Confidence</span>
        </div>
      </div>

      <div class="result-footer">
        <details class="features-details">
          <summary>Feature Summary</summary>
          <div class="features-grid">
            {#each Object.entries(result.features) as [key, value]}
              <div class="feature-item">
                <span class="label">{featureLabels[key] || key}</span>
                <span class="value feature-value">{typeof value === 'number' ? (integerFeatures.includes(key) ? Math.round(value) : value.toFixed(4)) : value}</span>
              </div>
            {/each}
          </div>
        </details>
        <button class="graph-btn" on:click={() => showGraph = true}>
          View Graph
        </button>
      </div>
    </div>
  {/if}
</div>

<TransactionGraph
  address={result?.address}
  visible={showGraph}
  on:close={() => showGraph = false}
  on:nodeClick={(event) => {
    showGraph = false;
    goToAddress(event.detail.address);
  }}
/>

<style>
  .classifier-container {
    width: 100%;
  }

  /* Search bar */
  .search-form {
    margin-bottom: 1.5rem;
  }

  .search-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 999px;
    background-color: var(--background-primary);
    padding: 0.4rem 0.5rem 0.4rem 1.25rem;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .search-bar:focus-within {
    border-color: var(--accent-color);
  }

  .search-bar.loading {
    border-color: var(--accent-color);
  }

  .search-icon {
    width: 20px;
    height: 20px;
    color: var(--text-secondary);
    flex-shrink: 0;
  }

  .search-bar input {
    flex-grow: 1;
    min-width: 0;
    border: none;
    background: transparent;
    padding: 0.5rem 0;
    font-size: 1rem;
    color: var(--text-primary);
  }

  .search-bar input:focus {
    outline: none;
  }

  ::placeholder {
    color: var(--text-secondary);
    opacity: 1;
  }

  .search-submit {
    background-color: var(--accent-color);
    color: white;
    border: none;
    padding: 0.5rem 1.25rem;
    font-size: 0.9rem;
    font-weight: 500;
    border-radius: 999px;
    cursor: pointer;
    flex-shrink: 0;
    transition: background-color 0.2s;
  }

  .search-submit:hover {
    background-color: var(--accent-color-hover);
  }

  .search-spinner {
    width: 20px;
    height: 20px;
    margin: 0.5rem 0.75rem;
    border: 2px solid var(--border-color);
    border-top-color: var(--accent-color);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    flex-shrink: 0;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-display {
    background-color: color-mix(in srgb, var(--error-color) 12%, var(--background-primary));
    color: var(--error-color);
    border: 1px solid color-mix(in srgb, var(--error-color) 40%, transparent);
    padding: 1rem;
    border-radius: 8px;
    animation: shake 0.5s ease-in-out;
  }

  .error-display p {
    margin: 0.25rem 0 0 0;
    color: var(--text-secondary);
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  /* Loading skeleton (theme-aware) */
  .loading-skeleton {
    border: 1px solid var(--border-color);
    border-radius: 12px;
    margin-top: 2rem;
    overflow: hidden;
    background: var(--background-primary);
  }

  .skeleton-body {
    padding: 1.5rem;
  }

  .skeleton-row {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .skeleton-circle {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .skeleton-gauge {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    margin-left: auto;
    flex-shrink: 0;
  }

  .skeleton-lines {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    flex-grow: 1;
    max-width: 260px;
  }

  .skeleton-line {
    height: 0.9rem;
    width: 100%;
  }

  .skeleton-line.short {
    width: 55%;
  }

  .skeleton-circle,
  .skeleton-gauge,
  .skeleton-line {
    background: linear-gradient(
      90deg,
      var(--background-secondary) 25%,
      var(--background-tertiary) 50%,
      var(--background-secondary) 75%
    );
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
  }

  .skeleton-circle,
  .skeleton-gauge {
    border-radius: 50%;
  }

  .skeleton-features {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr));
    gap: 1rem;
    padding: 1.5rem;
    border-top: 1px solid var(--border-color);
  }

  .skeleton-feature-item {
    padding: 0.75rem;
    background-color: var(--background-secondary);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  /* Result card */
  .result-card {
    border: 1px solid var(--border-color);
    border-radius: 12px;
    margin-top: 2rem;
    overflow: hidden;
    background-color: var(--background-primary);
  }

  .result-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    gap: 1.5rem;
  }

  .category-display {
    display: flex;
    align-items: center;
    gap: 1rem;
    min-width: 0;
  }

  .category-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 1.8rem;
    color: white;
    flex-shrink: 0;
  }

  .category-text {
    min-width: 0;
  }

  .category-text .label {
    font-size: 0.8rem;
    color: var(--text-secondary);
  }

  .model-badge {
    display: inline-block;
    margin-top: 0.35rem;
    font-size: 0.75rem;
    color: var(--text-secondary);
    background-color: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: 999px;
    padding: 0.15rem 0.6rem;
  }

  h2 {
    font-size: 1.5rem;
    margin: 0;
    font-weight: 600;
    color: var(--text-primary);
  }

  .result-side {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.25rem;
    flex-shrink: 0;
  }

  .gauge-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
  }

  .confidence-gauge {
    position: relative;
    width: 70px;
    height: 70px;
  }

  .gauge-svg {
    width: 100%;
    height: 100%;
  }

  .gauge-base {
    fill: none;
    stroke: var(--border-color);
    stroke-width: 3.8;
  }

  .gauge-arc {
    fill: none;
    stroke-width: 3.8;
    stroke-linecap: round;
  }

  .gauge-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
  }

  .gauge-text span {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-left: 2px;
  }

  .result-footer {
    position: relative;
    padding: 1rem 1.5rem;
    background-color: var(--background-secondary);
    border-top: 1px solid var(--border-color);
  }

  .graph-btn {
    position: absolute;
    top: 1rem;
    right: 1.5rem;
    background-color: transparent;
    color: var(--accent-color);
    border: 1.5px solid var(--border-color);
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    font-weight: 500;
    border-radius: 6px;
    cursor: pointer;
    flex-shrink: 0;
    transition: all 0.2s;
  }

  .graph-btn:hover {
    background-color: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
  }

  .features-details {
    min-width: 0;
  }

  .features-details summary {
    cursor: pointer;
    font-weight: 500;
    color: var(--text-secondary);
    outline: none;
    padding: 0.5rem 0;
    /* leave room for the absolutely-positioned View Graph button */
    padding-right: 8rem;
  }

  .features-details summary:hover {
    color: var(--text-primary);
  }

  .features-grid {
    margin-top: 0.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(200px, 100%), 1fr));
    gap: 1rem;
  }

  .feature-item {
    padding: 0.75rem;
    background-color: var(--background-tertiary);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .feature-item .label {
    font-size: 0.8rem;
    color: var(--text-secondary);
  }

  .feature-value {
    font-family: monospace;
    font-size: 0.9rem;
    color: var(--text-primary);
  }

  /* Responsive layout */
  @media (max-width: 600px) {
    .result-main {
      flex-direction: column;
      align-items: flex-start;
      gap: 1rem;
    }

    .result-side {
      align-self: center;
    }

    .graph-btn {
      position: static;
      display: block;
      width: 100%;
      margin-top: 1rem;
    }

    .features-details summary {
      padding-right: 0;
    }
  }
</style>
