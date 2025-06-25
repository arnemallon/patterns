<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let addressList = '';
  let isAnalyzing = false;
  let results = [];
  let showResults = false;
  let selectedFile = null;
  let dragOver = false;

  function handleAnalyze() {
    if (!addressList.trim()) return;
    
    isAnalyzing = true;
    showResults = false;
    
    // Parse addresses from input
    const addresses = addressList
      .split('\n')
      .map(addr => addr.trim())
      .filter(addr => addr.length > 0);
    
    // Simulate batch analysis
    setTimeout(() => {
      results = addresses.map((address, index) => ({
        id: index + 1,
        address: address,
        classification: Math.random() > 0.5 ? 'suspicious' : 'normal',
        risk_score: Math.random(),
        status: 'completed',
        timestamp: new Date()
      }));
      
      isAnalyzing = false;
      showResults = true;
    }, 2000);
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
      'Address,Classification,Risk Score,Status,Timestamp',
      ...results.map(r => `${r.address},${r.classification},${r.risk_score.toFixed(3)},${r.status},${r.timestamp.toISOString()}`)
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
  }

  function getRiskLevelColor(riskScore) {
    if (riskScore >= 0.7) return '#dc3545';
    if (riskScore >= 0.4) return '#ffc107';
    return '#28a745';
  }

  function getRiskLevelText(riskScore) {
    if (riskScore >= 0.7) return 'High';
    if (riskScore >= 0.4) return 'Medium';
    return 'Low';
  }

  function getClassificationIcon(classification) {
    return classification === 'suspicious' ? '⚠️' : '✅';
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
            <strong>{results.filter(r => r.classification === 'suspicious').length}</strong> suspicious
          </span>
          <span class="summary-item">
            <strong>{results.filter(r => r.classification === 'normal').length}</strong> normal
          </span>
        </div>
        <button class="export-btn" on:click={exportResults}>Export CSV</button>
      </div>
      <table class="results-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Address</th>
            <th>Classification</th>
            <th>Risk</th>
            <th>Status</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {#each results as r}
            <tr>
              <td>{r.id}</td>
              <td class="address-cell">{r.address}</td>
              <td class="classification-badge {r.classification}">{r.classification.charAt(0).toUpperCase() + r.classification.slice(1)}</td>
              <td class="risk-level-badge risk-{getRiskLevelText(r.risk_score).toLowerCase()}">{getRiskLevelText(r.risk_score)}</td>
              <td class="status-badge {r.status}">{r.status.charAt(0).toUpperCase() + r.status.slice(1)}</td>
              <td class="timestamp">{r.timestamp.toLocaleString()}</td>
            </tr>
          {/each}
        </tbody>
      </table>
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
    padding: var(--spacing-xl);
  }
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
    flex-wrap: wrap;
    gap: var(--spacing-md);
  }
  .results-header h2 {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    font-family: var(--font-family);
  }
  .results-summary {
    display: flex;
    gap: var(--spacing-lg);
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    font-family: var(--font-family);
  }
  .results-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: var(--spacing-lg);
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
  .results-table td.risk {
    font-weight: var(--font-weight-medium);
  }
  .results-table td.risk-high {
    color: var(--error-color);
  }
  .results-table td.risk-medium {
    color: var(--warning-color);
  }
  .results-table td.risk-low {
    color: var(--success-color);
  }
  .results-table td.status {
    font-weight: var(--font-weight-medium);
    color: var(--text-secondary);
  }
  .results-table td.timestamp {
    color: var(--text-tertiary);
    font-size: var(--font-size-xs);
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