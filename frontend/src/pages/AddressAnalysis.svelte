<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { useLocation } from 'svelte-routing';
  import AddressClassifier from '../components/AddressClassifier.svelte';
  import TransactionGraph from '../components/TransactionGraph.svelte';

  let addressToClassify = '';
  let showTransactionGraph = false;
  let currentAddress = '';
  let classificationResult = null;
  let showAddToCaseModal = false;
  let showGenerateReportModal = false;
  let availableCases = [];
  let selectedCase = null;
  let caseNote = '';

  const location = useLocation();

  onMount(() => {
    // Mock data for available cases
    availableCases = [
      { id: 1, name: 'Exchange Investigation', description: 'Investigating suspicious exchange activity' },
      { id: 2, name: 'Mixer Analysis', description: 'Tracking mixer service transactions' },
      { id: 3, name: 'Dark Web Monitoring', description: 'Monitoring known dark web addresses' }
    ];

    // Check for address parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const addressParam = urlParams.get('address');
    if (addressParam) {
      console.log('Found address in URL:', addressParam);
      addressToClassify = addressParam;
    }
  });

  // Watch for URL changes to update address when navigating
  $: {
    if (location.pathname === '/analysis') {
      const urlParams = new URLSearchParams(window.location.search);
      const addressParam = urlParams.get('address');
      if (addressParam && addressParam !== addressToClassify) {
        console.log('URL changed, new address:', addressParam);
        addressToClassify = addressParam;
        // Reset results when address changes
        classificationResult = null;
        currentAddress = '';
      }
    }
  }

  function handleClassificationComplete(event) {
    classificationResult = event.detail;
    currentAddress = addressToClassify;
  }

  function handleShowTransactionGraph() {
    showTransactionGraph = true;
  }

  function handleCloseTransactionGraph() {
    showTransactionGraph = false;
  }

  function handleNodeClick(event) {
    addressToClassify = event.detail.address;
    showTransactionGraph = false;
    // Trigger classification for the clicked address
  }

  function handleAddToCase() {
    showAddToCaseModal = true;
  }

  function handleGenerateReport() {
    showGenerateReportModal = true;
  }

  function handleAddToCaseSubmit() {
    if (selectedCase && caseNote) {
      // In real implementation, this would call an API
      console.log('Adding to case:', selectedCase, 'with note:', caseNote);
      showAddToCaseModal = false;
      selectedCase = null;
      caseNote = '';
    }
  }

  function handleGenerateReportSubmit() {
    // In real implementation, this would generate and download a report
    console.log('Generating report for:', currentAddress);
    showGenerateReportModal = false;
  }

  function getRiskLevelColor(riskScore) {
    if (riskScore >= 0.7) return 'var(--error-color)';
    if (riskScore >= 0.4) return 'var(--warning-color)';
    return 'var(--success-color)';
  }

  function getRiskLevelText(riskScore) {
    if (riskScore >= 0.7) return 'High Risk';
    if (riskScore >= 0.4) return 'Medium Risk';
    return 'Low Risk';
  }
</script>

<div class="address-analysis" in:fly={{ y: 20, duration: 500 }}>
  <!-- Main Analysis Section -->
  <div class="analysis-container">
    <AddressClassifier 
      bind:address={addressToClassify} 
      on:classificationComplete={handleClassificationComplete}
    />
  </div>

  <!-- Results Section -->
  {#if classificationResult}
    <div class="results-section" in:fade={{ duration: 300 }}>
      <div class="results-header">
        <h2>Analysis Results</h2>
        <div class="result-actions">
          <button class="btn btn-secondary" on:click={handleShowTransactionGraph}>
            View Transaction Graph
          </button>
          <button class="btn btn-primary" on:click={handleAddToCase}>
            Add to Case
          </button>
          <button class="btn btn-secondary" on:click={handleGenerateReport}>
            Generate Report
          </button>
        </div>
      </div>

      <div class="results-grid">
        <!-- Risk Assessment -->
        <div class="result-card">
          <div class="card-header">
            <h3>Risk Assessment</h3>
            <div class="risk-badge" style="background-color: {getRiskLevelColor(classificationResult.risk_score)}">
              {getRiskLevelText(classificationResult.risk_score)}
            </div>
          </div>
          <div class="risk-score">
            <div class="score-circle" style="border-color: {getRiskLevelColor(classificationResult.risk_score)}">
              <span class="score-value">{(classificationResult.risk_score * 100).toFixed(0)}%</span>
            </div>
          </div>
          <p class="risk-description">
            This address has been classified as <strong>{classificationResult.classification}</strong> 
            with a risk score of {(classificationResult.risk_score * 100).toFixed(1)}%.
          </p>
        </div>

        <!-- Feature Breakdown -->
        <div class="result-card">
          <div class="card-header">
            <h3>Feature Analysis</h3>
          </div>
          <div class="features-list">
            {#each Object.entries(classificationResult.features || {}) as [feature, value]}
              <div class="feature-item">
                <span class="feature-name">{feature.replace(/_/g, ' ').toUpperCase()}</span>
                <span class="feature-value">{typeof value === 'number' ? value.toFixed(3) : value}</span>
              </div>
            {/each}
          </div>
        </div>

        <!-- Address Information -->
        <div class="result-card">
          <div class="card-header">
            <h3>Address Information</h3>
          </div>
          <div class="address-info">
            <div class="info-item">
              <span class="info-label">Address:</span>
              <span class="info-value address">{currentAddress}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Analysis Date:</span>
              <span class="info-value">{new Date().toLocaleDateString()}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Total Transactions:</span>
              <span class="info-value">{classificationResult.total_transactions || 'N/A'}</span>
            </div>
            <div class="info-item">
              <span class="info-label">Balance:</span>
              <span class="info-value">{classificationResult.balance || 'N/A'} BTC</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Transaction Graph Modal -->
  {#if showTransactionGraph}
    <TransactionGraph 
      address={currentAddress}
      visible={showTransactionGraph}
      on:close={handleCloseTransactionGraph}
      on:nodeClick={handleNodeClick}
    />
  {/if}

  <!-- Add to Case Modal -->
  {#if showAddToCaseModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Add to Case</h3>
          <button class="modal-close" on:click={() => showAddToCaseModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="case-select">Select Case:</label>
            <select id="case-select" bind:value={selectedCase}>
              <option value={null}>Choose a case...</option>
              {#each availableCases as caseItem}
                <option value={caseItem.id}>{caseItem.name}</option>
              {/each}
            </select>
          </div>
          <div class="form-group">
            <label for="case-note">Note:</label>
            <textarea 
              id="case-note" 
              bind:value={caseNote}
              placeholder="Add a note about this address..."
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showAddToCaseModal = false}>
            Cancel
          </button>
          <button class="btn btn-primary" on:click={handleAddToCaseSubmit}>
            Add to Case
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Generate Report Modal -->
  {#if showGenerateReportModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Generate Report</h3>
          <button class="modal-close" on:click={() => showGenerateReportModal = false}>×</button>
        </div>
        <div class="modal-content">
          <p>Generate a detailed report for address <strong>{currentAddress}</strong>?</p>
          <p>This will include:</p>
          <ul>
            <li>Risk assessment and classification</li>
            <li>Feature analysis breakdown</li>
            <li>Transaction history summary</li>
            <li>Recommendations and next steps</li>
          </ul>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showGenerateReportModal = false}>
            Cancel
          </button>
          <button class="btn btn-primary" on:click={handleGenerateReportSubmit}>
            Generate Report
          </button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .address-analysis {
    max-width: 1200px;
    margin: 0 auto;
    font-family: var(--font-family);
    font-weight: var(--font-weight-normal);
    color: var(--text-primary);
  }

  .analysis-container {
    margin-bottom: var(--spacing-xl);
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
  }

  .results-section {
    margin-top: var(--spacing-xl);
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
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    font-family: var(--font-family);
    letter-spacing: -0.02em;
    line-height: var(--line-height-tight);
  }

  .result-actions {
    display: flex;
    gap: var(--spacing-md);
    flex-wrap: wrap;
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: var(--spacing-lg);
  }

  .result-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    font-family: var(--font-family);
    font-weight: var(--font-weight-normal);
    box-shadow: none;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }

  .card-header h3 {
    margin: 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    font-family: var(--font-family);
    letter-spacing: -0.02em;
    line-height: var(--line-height-tight);
  }

  .risk-badge {
    padding: var(--spacing-xs) var(--spacing-md);
    border-radius: var(--border-radius-md);
    color: white;
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-medium);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    background: none;
    border: 1px solid var(--border-color);
  }

  .risk-score {
    text-align: center;
    margin-bottom: var(--spacing-lg);
  }

  .score-circle {
    width: 120px;
    height: 120px;
    border: 4px solid;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto var(--spacing-md);
    background: var(--background-secondary);
    font-family: var(--font-family);
    font-weight: var(--font-weight-medium);
    box-shadow: none;
  }

  .score-value {
    font-size: var(--font-size-2xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    font-family: var(--font-family);
  }

  .risk-description {
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
    line-height: var(--line-height-normal);
    margin: 0;
    font-family: var(--font-family);
  }

  .features-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .feature-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-sm) 0;
    border-bottom: 1px solid var(--border-color-light);
    font-family: var(--font-family);
    font-weight: var(--font-weight-normal);
  }

  .feature-item:last-child {
    border-bottom: none;
  }

  .feature-name {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    font-weight: var(--font-weight-medium);
    font-family: var(--font-family);
  }

  .feature-value {
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    font-family: monospace;
  }

  .address-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .info-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    font-weight: var(--font-weight-medium);
    font-family: var(--font-family);
  }

  .info-value {
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    font-family: var(--font-family);
  }

  .info-value.address {
    font-family: monospace;
    background: var(--background-secondary);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius-sm);
  }

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: var(--spacing-lg);
  }

  .modal {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    max-width: 500px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
  }

  .modal-header h3 {
    margin: 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  .modal-close {
    background: none;
    border: none;
    font-size: var(--font-size-xl);
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: var(--border-radius-sm);
    transition: all var(--transition-fast);
  }

  .modal-close:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }

  .modal-content {
    padding: var(--spacing-lg);
  }

  .modal-content p {
    margin: 0 0 var(--spacing-md) 0;
    color: var(--text-secondary);
  }

  .modal-content ul {
    margin: 0 0 var(--spacing-lg) 0;
    padding-left: var(--spacing-lg);
    color: var(--text-secondary);
  }

  .modal-content li {
    margin-bottom: var(--spacing-xs);
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: var(--spacing-md);
    padding: var(--spacing-lg);
    border-top: 1px solid var(--border-color);
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .results-header {
      flex-direction: column;
      align-items: flex-start;
    }

    .result-actions {
      width: 100%;
      justify-content: flex-start;
    }

    .results-grid {
      grid-template-columns: 1fr;
    }

    .modal {
      margin: var(--spacing-md);
    }
  }

  .loading-spinner {
    display: inline-block;
    width: 32px;
    height: 32px;
    border: 4px solid #111;
    border-top: 4px solid #000;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto;
    background: #111;
  }
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
</style> 