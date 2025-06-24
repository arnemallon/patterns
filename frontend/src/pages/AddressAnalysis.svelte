<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
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

  onMount(() => {
    // Mock data for available cases
    availableCases = [
      { id: 1, name: 'Exchange Investigation', description: 'Investigating suspicious exchange activity' },
      { id: 2, name: 'Mixer Analysis', description: 'Tracking mixer service transactions' },
      { id: 3, name: 'Dark Web Monitoring', description: 'Monitoring known dark web addresses' }
    ];
  });

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
    if (riskScore >= 0.7) return '#dc3545';
    if (riskScore >= 0.4) return '#ffc107';
    return '#28a745';
  }

  function getRiskLevelText(riskScore) {
    if (riskScore >= 0.7) return 'High Risk';
    if (riskScore >= 0.4) return 'Medium Risk';
    return 'Low Risk';
  }
</script>

<div class="address-analysis" in:fly={{ y: 20, duration: 500 }}>
  <div class="page-header">
    <h1>Address Analysis</h1>
    <p>Analyze individual Bitcoin addresses for suspicious activity and risk assessment.</p>
  </div>

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
            <span class="btn-icon">📊</span>
            View Transaction Graph
          </button>
          <button class="btn btn-primary" on:click={handleAddToCase}>
            <span class="btn-icon">📁</span>
            Add to Case
          </button>
          <button class="btn btn-success" on:click={handleGenerateReport}>
            <span class="btn-icon">📄</span>
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
            <label for="case-note">Notes:</label>
            <textarea 
              id="case-note" 
              bind:value={caseNote} 
              placeholder="Add notes about this address..."
              rows="4"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showAddToCaseModal = false}>Cancel</button>
          <button class="btn btn-primary" on:click={handleAddToCaseSubmit}>Add to Case</button>
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
          <p>Generate a comprehensive report for address <strong>{currentAddress}</strong>?</p>
          <p>The report will include:</p>
          <ul>
            <li>Risk assessment and classification</li>
            <li>Feature analysis breakdown</li>
            <li>Transaction history summary</li>
            <li>Visual transaction graph</li>
            <li>Recommendations and next steps</li>
          </ul>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showGenerateReportModal = false}>Cancel</button>
          <button class="btn btn-success" on:click={handleGenerateReportSubmit}>Generate Report</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .address-analysis {
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

  .analysis-container {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
  }

  /* Results Section */
  .results-section {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
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

  .result-actions {
    display: flex;
    gap: 1rem;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
  }

  .btn-primary {
    background-color: #007bff;
    color: white;
  }

  .btn-primary:hover {
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

  /* Results Grid */
  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    padding: 1.5rem;
  }

  .result-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1.5rem;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }

  .card-header h3 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .risk-badge {
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .risk-score {
    text-align: center;
    margin: 1rem 0;
  }

  .score-circle {
    width: 80px;
    height: 80px;
    border: 4px solid;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto;
  }

  .score-value {
    font-size: 1.2rem;
    font-weight: 700;
  }

  .risk-description {
    margin: 0;
    color: #6c757d;
    font-size: 0.9rem;
  }

  /* Features List */
  .features-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .feature-item {
    display: flex;
    justify-content: space-between;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e9ecef;
  }

  .feature-name {
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.85rem;
  }

  .feature-value {
    font-family: monospace;
    color: #6c757d;
    font-size: 0.85rem;
  }

  /* Address Info */
  .address-info {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .info-label {
    font-weight: 500;
    color: #2c3e50;
  }

  .info-value {
    color: #6c757d;
  }

  .info-value.address {
    font-family: monospace;
    background-color: #e9ecef;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  /* Modal Styles */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 1rem;
  }

  .modal {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: #6c757d;
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-close:hover {
    color: #2c3e50;
  }

  .modal-content {
    padding: 1.5rem;
  }

  .modal-footer {
    padding: 1.5rem;
    border-top: 1px solid #e9ecef;
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
  }

  /* Form Styles */
  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #2c3e50;
  }

  .form-group select,
  .form-group textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: inherit;
  }

  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  /* Responsive Design */
  @media (max-width: 768px) {
    .results-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .result-actions {
      flex-direction: column;
    }

    .results-grid {
      grid-template-columns: 1fr;
    }

    .modal {
      margin: 1rem;
    }
  }
</style> 