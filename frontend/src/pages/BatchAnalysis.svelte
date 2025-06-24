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
  <div class="page-header">
    <h1>Batch Analysis</h1>
    <p>Analyze multiple Bitcoin addresses simultaneously for efficient investigation.</p>
  </div>

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
            <div class="drop-zone-icon">📁</div>
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
          <span class="btn-icon">🔍</span>
          Analyze Addresses
        {/if}
      </button>
      
      {#if showResults}
        <button class="btn btn-secondary" on:click={clearResults}>
          <span class="btn-icon">🗑️</span>
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
        <button class="btn btn-success" on:click={exportResults}>
          <span class="btn-icon">📥</span>
          Export CSV
        </button>
      </div>

      <div class="results-table">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Address</th>
              <th>Classification</th>
              <th>Risk Level</th>
              <th>Risk Score</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each results as result, index}
              <tr in:fade={{ delay: index * 50 }}>
                <td>{result.id}</td>
                <td>
                  <span class="address-cell">{result.address.substring(0, 12)}...</span>
                </td>
                <td>
                  <span class="classification-badge {result.classification}">
                    {getClassificationIcon(result.classification)}
                    {result.classification}
                  </span>
                </td>
                <td>
                  <span 
                    class="risk-level-badge"
                    style="background-color: {getRiskLevelColor(result.risk_score)}"
                  >
                    {getRiskLevelText(result.risk_score)}
                  </span>
                </td>
                <td>{(result.risk_score * 100).toFixed(1)}%</td>
                <td>
                  <span class="status-badge {result.status}">
                    {result.status}
                  </span>
                </td>
                <td>
                  <button class="action-btn" title="View Details">
                    👁️
                  </button>
                  <button class="action-btn" title="Add to Case">
                    📁
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  {/if}

  <!-- Instructions -->
  <div class="instructions">
    <h3>Instructions</h3>
    <div class="instructions-grid">
      <div class="instruction-item">
        <div class="instruction-icon">📝</div>
        <h4>Prepare Your Data</h4>
        <p>Ensure each Bitcoin address is on a separate line. You can include up to 100 addresses per batch.</p>
      </div>
      
      <div class="instruction-item">
        <div class="instruction-icon">🔍</div>
        <h4>Run Analysis</h4>
        <p>Click "Analyze Addresses" to process all addresses. The analysis may take a few minutes for large batches.</p>
      </div>
      
      <div class="instruction-item">
        <div class="instruction-icon">📊</div>
        <h4>Review Results</h4>
        <p>View the classification results, risk scores, and export the data for further analysis.</p>
      </div>
      
      <div class="instruction-item">
        <div class="instruction-icon">📁</div>
        <h4>Organize</h4>
        <p>Add suspicious addresses to cases for ongoing investigation and monitoring.</p>
      </div>
    </div>
  </div>
</div>

<style>
  .batch-analysis {
    max-width: 1200px;
    margin: 0 auto;
  }

  .page-header {
    margin-bottom: 2rem;
  }

  .page-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
    font-weight: 700;
    color: #2c3e50;
  }

  .page-header p {
    margin: 0;
    color: #6c757d;
    font-size: 1.1rem;
  }

  /* Input Section */
  .input-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 2rem;
    margin-bottom: 2rem;
  }

  .input-methods {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .input-method h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .input-method p {
    margin: 0 0 1rem 0;
    color: #6c757d;
    font-size: 0.9rem;
  }

  .address-input {
    width: 100%;
    padding: 1rem;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    font-family: monospace;
    font-size: 0.9rem;
    resize: vertical;
    transition: border-color 0.2s ease;
  }

  .address-input:focus {
    outline: none;
    border-color: #007bff;
  }

  /* File Drop Zone */
  .file-drop-zone {
    border: 2px dashed #ced4da;
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
    transition: all 0.2s ease;
    cursor: pointer;
  }

  .file-drop-zone:hover,
  .file-drop-zone.drag-over {
    border-color: #007bff;
    background-color: #f8f9ff;
  }

  .drop-zone-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
  }

  .drop-zone-icon {
    font-size: 2rem;
  }

  .file-upload-btn {
    background-color: #007bff;
    color: white;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: background-color 0.2s ease;
  }

  .file-upload-btn:hover {
    background-color: #0056b3;
  }

  /* Analysis Actions */
  .analysis-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-primary {
    background-color: #007bff;
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: #0056b3;
  }

  .btn-secondary {
    background-color: #6c757d;
    color: white;
  }

  .btn-secondary:hover {
    background-color: #545b62;
  }

  .btn-success {
    background-color: #28a745;
    color: white;
  }

  .btn-success:hover {
    background-color: #1e7e34;
  }

  .btn-icon {
    margin-right: 0.5rem;
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 0.5rem;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* Results Section */
  .results-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    margin-bottom: 2rem;
  }

  .results-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .results-header h2 {
    margin: 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .results-summary {
    display: flex;
    gap: 1.5rem;
  }

  .summary-item {
    color: #6c757d;
    font-size: 0.9rem;
  }

  /* Results Table */
  .results-table {
    overflow-x: auto;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th, td {
    padding: 1rem;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
  }

  th {
    background-color: #f8f9fa;
    font-weight: 600;
    color: #2c3e50;
    font-size: 0.9rem;
  }

  .address-cell {
    font-family: monospace;
    background-color: #f8f9fa;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .classification-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .classification-badge.suspicious {
    background-color: #fff3cd;
    color: #856404;
  }

  .classification-badge.normal {
    background-color: #d1edff;
    color: #0c5460;
  }

  .risk-level-badge {
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .status-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
  }

  .status-badge.completed {
    background-color: #d4edda;
    color: #155724;
  }

  .action-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.25rem;
    margin-right: 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .action-btn:hover {
    background-color: #f8f9fa;
  }

  /* Instructions */
  .instructions {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }

  .instructions h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .instructions-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .instruction-item {
    text-align: center;
    padding: 1.5rem;
    border-radius: 8px;
    background-color: #f8f9fa;
  }

  .instruction-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
  }

  .instruction-item h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .instruction-item p {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
    line-height: 1.5;
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .input-methods {
      grid-template-columns: 1fr;
    }

    .results-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .results-summary {
      justify-content: center;
    }

    .analysis-actions {
      flex-direction: column;
    }

    .instructions-grid {
      grid-template-columns: 1fr;
    }
  }
</style> 