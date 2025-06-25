<script>
  import { onMount, createEventDispatcher } from 'svelte';
  import { apiService } from '../services/api.js';
  import { fade, fly, scale } from 'svelte/transition';
  import TransactionGraph from './TransactionGraph.svelte';
  
  export let address = '';
  let result = null;
  let loading = false;
  let error = null;
  let showGraph = false;

  const dispatch = createEventDispatcher();

  // Watch for changes to the address prop and automatically submit
  $: if (address) {
    handleSubmit();
  }

  const featureLabels = {
    'PAIa11-1': 'Total Received',
    'PAIa11-2': 'Total Sent',
    'PAIa13': 'Received/Sent Ratio',
    'S2-1': 'Unique Senders (In-Degree)',
    'S2-2': 'Unique Recipients (Out-Degree)',
    'S2-3': 'Unique Counterparties',
    'CI2a32-2': 'Max Input/Total Ratio',
    'CI2a32-4': 'Max Output/Total Ratio'
  };
  
  const integerFeatures = ['S2-1', 'S2-2', 'S2-3'];
  
  async function handleSubmit() {
    if (!address.trim()) {
      error = { message: 'Validation Error', details: 'Please enter a Bitcoin address.' };
      return;
    }
    
    loading = true;
    error = null;
    result = null;
    
    try {
      result = await apiService.classifyAddress(address);
      dispatch('classificationComplete');
    } catch (err) {
      console.error("Caught error in component:", err);
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
    // Using a simple emoji for icons as an example.
    // In a real app, you might use an icon library.
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
</script>

<div class="classifier-container">
  <div class="header" in:fly={{ y: -20, duration: 300 }}>
    <h1>Bitcoin Address Classifier</h1>
    <p>A minimalist interface to analyze Bitcoin addresses.</p>
  </div>
  
  <form on:submit|preventDefault={handleSubmit} in:fly={{ y: 20, duration: 300, delay: 100 }}>
    <input
      type="text"
      bind:value={address}
      placeholder="Enter Bitcoin address..."
      disabled={loading}
      class:loading={loading}
    />
  </form>
  
  {#if error}
    <div class="error-display" in:fly={{ y: 20, duration: 300 }} out:fly={{ y: -20, duration: 200 }}>
      <strong>{error.message}</strong>
      {#if error.details}<p>{error.details}</p>{/if}
    </div>
  {/if}
  
  {#if loading}
    <div class="loading-skeleton" in:fly={{ y: 20, duration: 300 }}>
      <div class="skeleton-header">
        <div class="skeleton-title"></div>
      </div>
      <div class="skeleton-body">
        <div class="skeleton-item">
          <div class="skeleton-label"></div>
          <div class="skeleton-value"></div>
        </div>
        <div class="skeleton-item">
          <div class="skeleton-label"></div>
          <div class="skeleton-value"></div>
        </div>
      </div>
      <div class="skeleton-features">
        <div class="skeleton-feature-grid">
          {#each Array(8) as _, i}
            <div class="skeleton-feature-item">
              <div class="skeleton-feature-label"></div>
              <div class="skeleton-feature-value"></div>
            </div>
          {/each}
        </div>
      </div>
    </div>
  {/if}
  
  {#if result}
    <div class="result-card" in:scale={{ duration: 300, start: 0.95 }} out:scale={{ duration: 150 }}>
      <div class="result-main">
        <div class="category-display">
          {#if categoryInfo}
            <div class="category-icon" style="background-color: {categoryInfo.color}; box-shadow: none;">
              <span class="icon">{categoryInfo.icon}</span>
            </div>
          {/if}
          <div class="category-text">
            <span class="label">Classification Result</span>
            <h2>{getCategoryDescription(result.classification)}</h2>
          </div>
        </div>
        <div class="confidence-gauge">
          <svg class="gauge-svg" viewBox="0 0 36 36">
            <path class="gauge-base" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
            <path 
              class="gauge-arc" 
              stroke="{confidenceColor}"
              stroke-dasharray="{result.confidence * 100}, 100"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            ></path>
          </svg>
          <div class="gauge-text">
            {(result.confidence * 100).toFixed(0)}<span>%</span>
          </div>
        </div>
      </div>
      <div class="result-footer">
        <div class="footer-item address-item">
          <span class="label">Address</span>
          <span class="value"><code>{result.address}</code></span>
        </div>
        <div class="footer-item action-item">
          <button class="graph-btn" on:click={() => showGraph = true}>
            View Graph
          </button>
        </div>
      </div>

      <details class="features-details">
        <summary>Show Feature Summary</summary>
        <div class="features-grid">
          {#each Object.entries(result.features) as [key, value]}
            <div class="feature-item">
              <span class="label">{featureLabels[key] || key}</span>
              <span class="value feature-value">{typeof value === 'number' ? (integerFeatures.includes(key) ? value : value.toFixed(4)) : value}</span>
            </div>
          {/each}
        </div>
      </details>
    </div>
  {/if}
</div>

<TransactionGraph 
  address={result?.address} 
  visible={showGraph} 
  on:close={() => showGraph = false}
  on:nodeClick={(event) => {
    address = event.detail.address;
    showGraph = false;
  }}
/>

<style>
  .classifier-container {
    width: 100%;
  }

  .header {
    text-align: center;
    margin-bottom: 2.5rem;
  }

  h1 {
    font-size: 2rem;
    font-weight: 600;
    margin: 0 0 0.5rem 0;
  }

  p {
    color: #6c757d;
    margin: 0;
  }

  form {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  input {
    flex-grow: 1;
    border: 1px solid var(--border-color);
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 6px;
    background-color: var(--background-primary);
    color: var(--text-primary);
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  input:focus {
    outline: none;
    border-color: var(--accent-color);
    box-shadow: none;
  }

  input.loading {
    border-color: var(--accent-color);
    background-color: var(--background-secondary);
  }

  ::placeholder {
    color: var(--text-secondary);
    opacity: 1;
  }

  button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1rem;
    font-weight: 500;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    min-width: 120px;
    justify-content: center;
  }

  button:hover:not(:disabled) {
    background-color: #0056b3;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  button:disabled {
    background-color: #adb5bd;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }

  button:focus {
    outline: 2px solid var(--accent-color);
    outline-offset: 2px;
    box-shadow: none;
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid var(--accent-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .error-display {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
    padding: 1rem;
    border-radius: 6px;
    animation: shake 0.5s ease-in-out;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  /* Loading Skeleton Styles */
  .loading-skeleton {
    border: 1px solid var(--border-color-light);
    border-radius: 8px;
    margin-top: 2rem;
    overflow: hidden;
    background: var(--background-secondary);
  }

  .skeleton-header {
    padding: 1rem 1.5rem;
    background-color: var(--background-secondary);
    border-bottom: 1px solid var(--border-color);
  }

  .skeleton-title, .skeleton-label, .skeleton-value, .skeleton-feature-label, .skeleton-feature-value {
    background: linear-gradient(90deg, var(--background-tertiary) 25%, var(--background-secondary) 50%, var(--background-tertiary) 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
  }

  .skeleton-body {
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .skeleton-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .skeleton-feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .skeleton-feature-item {
    padding: 0.75rem;
    background-color: #f8f9fa;
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .skeleton-feature-label {
    height: 0.8rem;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
    width: 80%;
  }

  .skeleton-feature-value {
    height: 0.8rem;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
    width: 60%;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  .result-card {
    border: 1px solid var(--border-color);
    border-radius: 12px;
    margin-top: 2rem;
    overflow: hidden;
    background-color: var(--background-primary);
    box-shadow: none;
    transition: box-shadow 0.3s ease;
  }
  .result-card:hover {
    box-shadow: none;
  }

  .result-main {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem;
    gap: 1.5rem;
    background: var(--background-primary);
  }
  
  .category-display {
    display: flex;
    align-items: center;
    gap: 1rem;
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
    background: var(--background-primary);
    box-shadow: none;
  }
  
  .category-text .label {
    font-size: 0.8rem;
    color: #888;
  }
  
  h2 {
    font-size: 1.5rem;
    margin: 0;
    font-weight: 600;
  }

  .confidence-gauge {
    position: relative;
    width: 70px;
    height: 70px;
    flex-shrink: 0;
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
    transform: rotate(-90deg);
    transform-origin: 50% 50%;
    transition: stroke-dasharray 0.5s ease-in-out;
  }

  .gauge-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.25rem;
    font-weight: 600;
  }
  .gauge-text span {
    font-size: 0.8rem;
    color: #888;
    margin-left: 2px;
  }

  .result-footer {
    padding: 1rem 1.5rem;
    background-color: var(--background-secondary);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    box-shadow: none;
  }

  .footer-item {
    display: flex;
    flex-direction: column;
  }
  
  .footer-item .label { font-size: 0.75rem; color: var(--text-secondary); }
  .footer-item.address-item .value code {
    background-color: transparent;
    padding: 0;
    font-size: 0.9em;
    word-break: break-all;
    color: var(--text-primary);
  }
  
  .footer-item.address-item .value code:focus {
    outline: none;
    box-shadow: none;
  }
  
  .action-item {
    align-items: flex-end;
  }

  .graph-btn {
    background-color: transparent;
    color: var(--accent-color);
    border: 1.5px solid var(--border-color);
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    font-weight: 500;
    border-radius: 6px;
    cursor: pointer;
  }

  .graph-btn:hover {
    background-color: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
  }
  
  .features-details {
    padding: 1rem 1.5rem;
    border-top: 1px solid var(--border-color);
  }

  .features-details summary {
    cursor: pointer;
    font-weight: 500;
    color: #495057;
    outline: none;
    padding-bottom: 0.5rem;
  }

  .features-grid {
    margin-top: 0.5rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
  }
  
  .feature-item {
    padding: 0.75rem;
    background-color: var(--background-tertiary);
    border-radius: 6px;
  }

  .feature-item .label {
    text-transform: none;
    letter-spacing: 0;
    font-size: 0.8rem;
  }
  
  .feature-value {
    font-family: monospace;
    font-size: 0.9rem;
  }
</style> 