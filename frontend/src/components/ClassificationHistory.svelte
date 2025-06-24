<script>
  import { onMount, createEventDispatcher, onDestroy } from 'svelte';
  import { apiService } from '../services/api.js';
  import { fly, fade, scale } from 'svelte/transition';
  
  let classifications = [];
  let loading = true;
  let error = null;
  let intervalId;
  
  // Pagination state
  let currentPage = 1;
  let limit = 10;
  let totalItems = 0;
  $: totalPages = Math.ceil(totalItems / limit);
  
  const dispatch = createEventDispatcher();
  
  onMount(async () => {
    await loadHistory();
    intervalId = setInterval(loadHistory, 10000); // Poll every 10 seconds
  });

  onDestroy(() => {
    if (intervalId) {
      clearInterval(intervalId);
    }
  });
  
  export async function loadHistory(resetPage = false) {
    if (resetPage) {
      currentPage = 1;
    }

    loading = true;
    error = null;
    try {
      const offset = (currentPage - 1) * limit;
      const response = await apiService.getHistory(limit, offset);
      classifications = response.classifications;
      totalItems = response.total;
    } catch (err) {
      error = err.message || 'Failed to load history';
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
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleString('en-US', { 
        year: 'numeric', month: 'short', day: 'numeric', 
        hour: 'numeric', minute: '2-digit' 
    });
  }
  
  function formatAddress(address) {
    return `${address.substring(0, 12)}...${address.substring(address.length - 8)}`;
  }

  function handleAddressClick(address) {
    dispatch('classify', address);
  }

  function nextPage() {
    if (currentPage < totalPages) {
      currentPage++;
      loadHistory();
    }
  }

  function prevPage() {
    if (currentPage > 1) {
      currentPage--;
      loadHistory();
    }
  }
</script>

<div class="history-container" in:fly={{ y: 20, duration: 300 }}>
    <div class="header">
        <h2>Classification History</h2>
        {#if loading}
          <div class="loading-indicator">
            <div class="loading-spinner"></div>
            <span>Updating...</span>
          </div>
        {/if}
    </div>
  
  {#if error}
    <div class="error-display" in:fly={{ y: 20, duration: 300 }} out:fly={{ y: -20, duration: 200 }}>
      {error}
    </div>
  {/if}

  <div class="table-container">
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Address</th>
                <th>Category</th>
                <th class="confidence-col">Confidence</th>
            </tr>
        </thead>
        <tbody>
            {#if loading && classifications.length === 0}
                {#each Array(5) as _, i}
                  <tr class="skeleton-row" in:fly={{ y: 20, duration: 300, delay: i * 100 }}>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                    <td><div class="skeleton-cell"></div></td>
                  </tr>
                {/each}
            {:else if classifications.length === 0}
                 <tr><td colspan="4" class="status-cell">No history found.</td></tr>
            {:else}
                {#each classifications as item, i}
                    <tr 
                      class="history-item" 
                      on:click={() => handleAddressClick(item.address)} 
                      title="Click to re-classify this address"
                      in:fly={{ y: 20, duration: 300, delay: i * 50 }}
                      out:fly={{ y: -20, duration: 200 }}
                    >
                        <td class="date-cell">{formatDate(item.created_at)}</td>
                        <td><code title={item.address}>{formatAddress(item.address)}</code></td>
                        <td>{getCategoryDescription(item.classification)}</td>
                        <td class="confidence-col">{(item.confidence * 100).toFixed(1)}%</td>
                    </tr>
                {/each}
            {/if}
        </tbody>
    </table>
  </div>

  {#if totalPages > 1}
    <div class="pagination-controls" in:fly={{ y: 20, duration: 300 }}>
        <button on:click={prevPage} disabled={currentPage === 1 || loading}>
            &larr; Previous
        </button>
        <span>Page {currentPage} of {totalPages}</span>
        <button on:click={nextPage} disabled={currentPage >= totalPages || loading}>
            Next &rarr;
        </button>
    </div>
  {/if}
</div>

<style>
  .history-container {
    border: 1px solid #e9ecef;
    border-radius: 8px;
  }

  .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem;
      border-bottom: 1px solid #e9ecef;
  }

  h2 {
    font-size: 1.25rem;
    margin: 0;
    font-weight: 500;
  }

  .loading-indicator {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #6c757d;
    font-size: 0.9rem;
  }

  .loading-spinner {
    width: 12px;
    height: 12px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .table-container {
      width: 100%;
      overflow-x: auto;
  }

  table {
      width: 100%;
      border-collapse: collapse;
  }

  th, td {
      padding: 1rem 1.5rem;
      text-align: left;
      border-bottom: 1px solid #f1f3f5;
  }
  
  tbody tr:last-child td {
      border-bottom: none;
  }

  thead th {
      color: #6c757d;
      font-size: 0.8rem;
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      background-color: #f8f9fa;
  }
  
  td {
      color: #495057;
      font-size: 0.95rem;
  }
  
  td code {
    background-color: #f1f3f5;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: monospace;
    transition: background-color 0.2s;
  }
  
  .history-item:hover td code {
    background-color: #e9ecef;
  }
  
  .confidence-col {
      text-align: right;
  }
  
  .date-cell {
      white-space: nowrap;
      color: #6c757d;
  }

  .status-cell {
      text-align: center;
      color: #6c757d;
      padding: 2.5rem;
      font-style: italic;
  }

  .error-display {
    padding: 1rem 1.5rem;
    background-color: #f8d7da;
    color: #721c24;
    animation: shake 0.5s ease-in-out;
  }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }

  /* Skeleton Loading Styles */
  .skeleton-row {
    animation: pulse 1.5s ease-in-out infinite;
  }

  .skeleton-cell {
    height: 1rem;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
    width: 100%;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.7; }
  }

  .history-item {
    cursor: pointer;
    transition: all 0.2s;
  }

  .history-item:hover {
    background-color: #f8f9fa;
    transform: translateX(4px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .pagination-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem 1.5rem;
    border-top: 1px solid #e9ecef;
    gap: 1rem;
    user-select: none;
  }

  .pagination-controls button {
    background-color: #fff;
    color: #007bff;
    border: 1px solid #dee2e6;
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
    font-weight: 500;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .pagination-controls button:hover:not(:disabled) {
    background-color: #f8f9fa;
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .pagination-controls button:disabled {
    color: #6c757d;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  .pagination-controls span {
    color: #6c757d;
    font-size: 0.9rem;
  }
</style> 