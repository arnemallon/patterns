<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { apiService } from '../services/api.js';

  let addressList = '';
  let isAnalyzing = false;
  let results = [];
  let showResults = false;
  let selectedFile = null;
  let dragOver = false;
  let error = null;



  async function handleAnalyze() {
    if (!addressList.trim()) return;
    
    isAnalyzing = true;
    showResults = false;
    error = null;
    
    // Parse addresses from input
    const addresses = addressList
      .split('\n')
      .map(addr => addr.trim())
      .filter(addr => addr.length > 0);
    
    try {
      const response = await apiService.batchClassifyAddresses(addresses);
      results = response.results.map((result, index) => ({
        id: index + 1,
        address: result.address,
        classification: result.classification,
        confidence: result.confidence,
        status: result.status === 'success' ? 'completed' : result.status,
        error: result.error,
        cached: result.cached || false
      }));
      
      showResults = true;
    } catch (err) {
      error = err.message || 'Batch analysis failed';
      console.error('Batch analysis error:', err);
    } finally {
      isAnalyzing = false;
    }
  }

  function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file && file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (e) => {
        addressList = e.target.result;
      };
      reader.readAsText(file);
    }
  }

  function handleDragOver(event) {
    event.preventDefault();
    dragOver = true;
  }

  function handleDragLeave(event) {
    event.preventDefault();
    dragOver = false;
  }

  function handleDrop(event) {
    event.preventDefault();
    dragOver = false;
    
    const file = event.dataTransfer.files[0];
    if (file && file.type === 'text/plain') {
      const reader = new FileReader();
      reader.onload = (e) => {
        addressList = e.target.result;
      };
      reader.readAsText(file);
    }
  }

  function exportResults() {
    const csvContent = [
      'Address,Status,Classification,Confidence',
      ...results.map(r => {
        const classification = r.classification !== null ? getCategoryDescription(r.classification) : 'Unknown';
        const confidence = r.confidence !== null ? `${(r.confidence * 100).toFixed(1)}%` : '-';
        return `${r.address},${r.status},${classification},${confidence}`;
      })
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'batch_analysis_results.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  }

  function clearResults() {
    results = [];
    showResults = false;
    addressList = '';
    error = null;
  }

  function getCategoryDescription(prediction) {
    if (prediction === null || prediction === undefined) {
      return 'Unknown';
    }
    
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

  function formatAddress(address) {
    return `${address.substring(0, 12)}...${address.substring(address.length - 8)}`;
  }
</script>

<div class="batch-analysis" in:fly={{ y: 20, duration: 500 }}>
  <!-- Input Section -->
  <div class="input-section">
    <div class="input-methods">
      <!-- Text Input -->
      <div class="input-method">
        <h3>Enter Addresses</h3>
        <p>Paste Bitcoin addresses, one per line:</p>
        <textarea 
          bind:value={addressList}
          placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&#10;3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy&#10;..."
          rows="10"
          class="address-input"
        ></textarea>
      </div>

      <!-- File Upload -->
      <div class="input-method">
        <h3>Upload File</h3>
        <p>Upload a text file with addresses (one per line):</p>
        <div 
          class="file-drop-zone"
          class:drag-over={dragOver}
          on:dragover={handleDragOver}
          on:dragleave={handleDragLeave}
          on:drop={handleDrop}
        >
          <div class="drop-zone-content">
            <p>Drag and drop a text file here, or</p>
            <label for="file-upload" class="file-upload-btn">Choose File</label>
            <input 
              id="file-upload" 
              type="file" 
              accept=".txt,.csv" 
              on:change={handleFileUpload}
              style="display: none;"
            />
          </div>
        </div>
      </div>
    </div>

    <div class="analysis-actions">
      <button 
        class="btn btn-primary" 
        on:click={handleAnalyze}
        disabled={!addressList.trim() || isAnalyzing}
      >
        {#if isAnalyzing}
          <span class="loading-spinner"></span>
          Analyzing...
        {:else}
          Analyze Addresses
        {/if}
      </button>
      

      
      {#if showResults}
        <button class="btn btn-secondary" on:click={clearResults}>
          Clear Results
        </button>
      {/if}
    </div>
  </div>

  <!-- Error Display -->
  {#if error}
    <div class="error-display" in:fly={{ y: 20, duration: 300 }}>
      <strong>Error:</strong> {error}
      <button class="clear-error-btn" on:click={() => error = null}>×</button>
    </div>
  {/if}

  <!-- Results Section -->
  {#if showResults}
    <div class="results-section" in:fade={{ duration: 300 }}>
      <div class="results-header">
        <h2>Analysis Results</h2>
        <div class="results-summary">
          <span class="summary-item">
            <strong>{results.length}</strong> addresses analyzed
          </span>
          <span class="summary-item">
            <strong>{results.filter(r => r.status === 'completed').length}</strong> successful
          </span>
          <span class="summary-item">
            <strong>{results.filter(r => r.status === 'error').length}</strong> errors
          </span>
        </div>
        <button class="export-btn" on:click={exportResults}>Export CSV</button>
      </div>
      
      <div class="table-container">
        <table class="results-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Address</th>
              <th>Status</th>
              <th>Category</th>
              <th>Confidence</th>
            </tr>
          </thead>
          <tbody>
            {#each results as r, i}
              <tr class={i % 2 === 0 ? 'even-row' : 'odd-row'}>
                <td>{r.id}</td>
                <td><code title={r.address}>{formatAddress(r.address)}</code></td>
                <td class="status-col">
                  <span class="status-badge {r.status}">
                    {r.status === 'completed' ? '✓' : '✗'}
                  </span>
                </td>
                <td class="category-col">
                  {#if r.status === 'completed' && r.classification !== null}
                    {getCategoryDescription(r.classification)}
                  {:else if r.status === 'completed' && r.classification === null}
                    <span class="error-text">No classification</span>
                  {:else}
                    <span class="error-text" title={r.error || 'Unknown error'}>
                      {r.error ? (r.error.length > 30 ? r.error.substring(0, 30) + '...' : r.error) : 'Error'}
                    </span>
                  {/if}
                </td>
                <td class="confidence-col">
                  {#if r.status === 'completed' && r.confidence !== null}
                    {(r.confidence * 100).toFixed(1)}%
                  {:else}
                    -
                  {/if}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}
</div>

<style>
  .batch-analysis {
    max-width: 1200px;
    margin: 0 auto;
    font-family: var(--font-family);
    color: var(--text-primary);
    font-weight: var(--font-weight-normal);
  }
  .input-section {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xl);
  }
  .input-methods {
    display: flex;
    gap: var(--spacing-xl);
    flex-wrap: wrap;
  }
  .input-method {
    flex: 1 1 300px;
    min-width: 280px;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }
  .input-method h3 {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-medium);
    margin: 0 0 var(--spacing-xs) 0;
    color: var(--text-primary);
    font-family: var(--font-family);
  }
  .input-method p {
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    margin: 0 0 var(--spacing-xs) 0;
    font-family: var(--font-family);
  }
  .address-input {
    width: 100%;
    min-height: 180px;
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-md);
    font-size: var(--font-size-base);
    font-family: var(--font-family);
    color: var(--text-primary);
    background: var(--background-secondary);
    resize: vertical;
    transition: border-color 0.2s;
  }
  .address-input:focus {
    outline: none;
    border-color: var(--accent-color);
  }
  .file-drop-zone {
    border: 2px dashed var(--border-color);
    border-radius: var(--border-radius-md);
    background: var(--background-secondary);
    padding: var(--spacing-xl);
    text-align: center;
    transition: border-color 0.2s, background 0.2s;
    cursor: pointer;
  }
  .file-drop-zone.drag-over {
    border-color: var(--accent-color);
    background: var(--background-tertiary);
  }
  .drop-zone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-sm);
  }
  .file-upload-btn {
    color: var(--accent-color);
    cursor: pointer;
    text-decoration: underline;
    font-size: var(--font-size-sm);
    font-family: var(--font-family);
    background: none;
    border: none;
    padding: 0;
  }
  .analysis-actions {
    display: flex;
    gap: var(--spacing-md);
    align-items: center;
    margin-top: var(--spacing-md);
  }
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-sm) var(--spacing-lg);
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--border-color);
    background: var(--background-primary);
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    letter-spacing: 0.01em;
  }
  .btn-primary {
    background: var(--accent-color);
    color: white;
    border-color: var(--accent-color);
  }
  .btn-primary:disabled {
    background: var(--border-color);
    color: var(--text-tertiary);
    border-color: var(--border-color);
    cursor: not-allowed;
  }
  .btn-secondary {
    background: var(--background-secondary);
    color: var(--accent-color);
    border-color: var(--accent-color);
  }
  .btn-secondary:hover {
    background: var(--background-tertiary);
    color: white;
  }
  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid var(--accent-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: var(--spacing-xs);
  }
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  .results-section {
    margin-top: var(--spacing-xl);
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
  }
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0;
    flex-wrap: wrap;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
  }
  .results-header h2 {
    margin: 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    font-family: var(--font-family);
  }
  .results-summary {
    display: flex;
    gap: var(--spacing-lg);
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    font-family: var(--font-family);
    font-weight: var(--font-weight-normal);
  }
  .results-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-family);
  }
  .results-table th, .results-table td {
    padding: var(--spacing-md);
    border-bottom: 1px solid var(--border-color);
    text-align: left;
    font-size: var(--font-size-sm);
  }
  .results-table th {
    color: var(--text-secondary);
    font-weight: var(--font-weight-medium);
    background: var(--background-secondary);
    text-transform: uppercase;
    letter-spacing: 0.03em;
  }
  .results-table tr:nth-child(even) td {
    background: var(--background-secondary);
  }
  .results-table tr:nth-child(odd) td {
    background: var(--background-primary);
  }
  
  .table-container {
    width: 100%;
    background: var(--background-primary);
    margin: 0;
    padding: 0;
  }
  
  .category-col {
    color: var(--accent-color);
    font-weight: var(--font-weight-medium);
  }
  
  .confidence-col {
    color: var(--accent-color);
    font-weight: var(--font-weight-medium);
  }

  .error-text {
    color: #dc3545;
    font-weight: var(--font-weight-medium);
  }
  

  
  .error-display {
    padding: 1rem 1.5rem;
    background-color: #f8d7da;
    color: #721c24;
    border-radius: var(--border-radius-md);
    margin-bottom: var(--spacing-lg);
    animation: shake 0.5s ease-in-out;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .clear-error-btn {
    background: none;
    border: none;
    color: #721c24;
    font-size: 18px;
    cursor: pointer;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
  }

  .clear-error-btn:hover {
    background: rgba(114, 28, 36, 0.1);
  }
  
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-5px); }
    75% { transform: translateX(5px); }
  }
  .export-btn {
    background: var(--background-secondary);
    color: var(--accent-color);
    border: 1px solid var(--accent-color);
    font-weight: var(--font-weight-medium);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-sm) var(--spacing-lg);
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
  }
  .export-btn:hover {
    background: var(--accent-color);
    color: white;
  }
  .results-table td.risk-level-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
  }
  .results-table td.risk-level-badge.risk-high {
    background-color: var(--error-color);
    color: white;
  }
  .results-table td.risk-level-badge.risk-medium {
    background-color: var(--warning-color);
    color: white;
  }
  .results-table td.risk-level-badge.risk-low {
    background-color: var(--success-color);
    color: white;
  }
  .results-table td.status-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
  }
  .results-table td.status-badge.completed {
    background-color: var(--success-color);
    color: white;
  }

  .status-badge.error {
    background-color: var(--error-color);
    color: white;
  }

  .status-col {
    text-align: center;
  }
  .results-table td.action-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    margin-right: 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }
  .results-table td.action-btn:hover {
    background-color: var(--background-secondary);
  }
  .results-table td.address-cell {
    font-family: monospace;
    background-color: var(--background-secondary);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }
  .results-table td.classification-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
  }
  .results-table td.classification-badge.suspicious {
    background-color: var(--error-color);
    color: white;
  }
  .results-table td.classification-badge.normal {
    background-color: var(--success-color);
    color: white;
  }
  @media (max-width: 768px) {
    .input-methods {
      flex-direction: column;
    }
    .results-header {
      flex-direction: column;
      gap: var(--spacing-md);
      align-items: stretch;
    }
    .results-summary {
      justify-content: center;
    }
    .analysis-actions {
      flex-direction: column;
    }
  }
  .btn-primary,
  .btn-primary:hover,
  .btn-primary:focus {
    color: #fff !important;
  }
</style> 