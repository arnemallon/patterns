<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';

  let cases = [];
  let selectedCase = null;
  let showCreateCaseModal = false;
  let showAddAddressModal = false;
  let newCaseName = '';
  let newCaseDescription = '';
  let newAddress = '';
  let newNote = '';

  onMount(() => {
    // Mock data
    cases = [
      {
        id: 1,
        name: 'Exchange Investigation',
        description: 'Investigating suspicious exchange activity',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3), // 3 days ago
        addresses: [
          {
            id: 1,
            address: '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',
            classification: 'suspicious',
            risk_score: 0.85,
            note: 'Known mixer address',
            added_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2)
          },
          {
            id: 2,
            address: '3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy',
            classification: 'normal',
            risk_score: 0.23,
            note: 'Exchange hot wallet',
            added_at: new Date(Date.now() - 1000 * 60 * 60 * 24)
          }
        ]
      },
      {
        id: 2,
        name: 'Mixer Analysis',
        description: 'Tracking mixer service transactions',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 7), // 7 days ago
        addresses: [
          {
            id: 3,
            address: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
            classification: 'suspicious',
            risk_score: 0.92,
            note: 'High volume mixer output',
            added_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5)
          }
        ]
      }
    ];
  });

  function handleCreateCase() {
    if (newCaseName.trim()) {
      const newCase = {
        id: cases.length + 1,
        name: newCaseName,
        description: newCaseDescription,
        created_at: new Date(),
        addresses: []
      };
      cases = [...cases, newCase];
      showCreateCaseModal = false;
      newCaseName = '';
      newCaseDescription = '';
    }
  }

  function handleAddAddress() {
    if (selectedCase && newAddress.trim()) {
      const addressData = {
        id: Date.now(),
        address: newAddress,
        classification: Math.random() > 0.5 ? 'suspicious' : 'normal',
        risk_score: Math.random(),
        note: newNote,
        added_at: new Date()
      };
      
      selectedCase.addresses = [...selectedCase.addresses, addressData];
      cases = cases.map(c => c.id === selectedCase.id ? selectedCase : c);
      
      showAddAddressModal = false;
      newAddress = '';
      newNote = '';
    }
  }

  function handleDeleteCase(caseId) {
    if (confirm('Are you sure you want to delete this case?')) {
      cases = cases.filter(c => c.id !== caseId);
      if (selectedCase && selectedCase.id === caseId) {
        selectedCase = null;
      }
    }
  }

  function handleDeleteAddress(addressId) {
    if (selectedCase) {
      selectedCase.addresses = selectedCase.addresses.filter(a => a.id !== addressId);
      cases = cases.map(c => c.id === selectedCase.id ? selectedCase : c);
    }
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

  function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  }
</script>

<div class="case-management" in:fly={{ y: 20, duration: 500 }}>
  <div class="page-header">
    <h1>Case Management</h1>
    <p>Organize your investigations into cases with addresses, notes, and analysis results.</p>
  </div>

  <div class="case-layout">
    <!-- Cases List -->
    <div class="cases-sidebar">
      <div class="sidebar-header">
        <h2>Cases</h2>
        <button class="btn btn-primary" on:click={() => showCreateCaseModal = true}>
          <span class="btn-icon">➕</span>
          New Case
        </button>
      </div>
      
      <div class="cases-list">
        {#each cases as caseItem}
          <div 
            class="case-item"
            class:active={selectedCase && selectedCase.id === caseItem.id}
            on:click={() => selectedCase = caseItem}
          >
            <div class="case-info">
              <h3>{caseItem.name}</h3>
              <p>{caseItem.description}</p>
              <div class="case-meta">
                <span class="address-count">{caseItem.addresses.length} addresses</span>
                <span class="case-date">{formatDate(caseItem.created_at)}</span>
              </div>
            </div>
            <button 
              class="delete-btn"
              on:click|stopPropagation={() => handleDeleteCase(caseItem.id)}
              title="Delete case"
            >
              🗑️
            </button>
          </div>
        {/each}
      </div>
    </div>

    <!-- Case Detail -->
    <div class="case-detail">
      {#if selectedCase}
        <div class="detail-header">
          <div class="case-title">
            <h2>{selectedCase.name}</h2>
            <p>{selectedCase.description}</p>
          </div>
          <div class="case-actions">
            <button class="btn btn-primary" on:click={() => showAddAddressModal = true}>
              <span class="btn-icon">➕</span>
              Add Address
            </button>
            <button class="btn btn-secondary">
              <span class="btn-icon">📄</span>
              Export Case
            </button>
          </div>
        </div>

        <div class="addresses-section">
          <h3>Addresses ({selectedCase.addresses.length})</h3>
          
          {#if selectedCase.addresses.length > 0}
            <div class="addresses-grid">
              {#each selectedCase.addresses as address}
                <div class="address-card" in:fade={{ delay: address.id * 50 }}>
                  <div class="address-header">
                    <span class="address-text">{address.address.substring(0, 12)}...</span>
                    <button 
                      class="delete-btn small"
                      on:click={() => handleDeleteAddress(address.id)}
                      title="Remove address"
                    >
                      ×
                    </button>
                  </div>
                  
                  <div class="address-details">
                    <div class="classification-badge {address.classification}">
                      {address.classification === 'suspicious' ? '⚠️' : '✅'}
                      {address.classification}
                    </div>
                    
                    <div class="risk-info">
                      <span 
                        class="risk-badge"
                        style="background-color: {getRiskLevelColor(address.risk_score)}"
                      >
                        {getRiskLevelText(address.risk_score)} Risk
                      </span>
                      <span class="risk-score">{(address.risk_score * 100).toFixed(0)}%</span>
                    </div>
                    
                    {#if address.note}
                      <div class="address-note">
                        <strong>Note:</strong> {address.note}
                      </div>
                    {/if}
                    
                    <div class="address-date">
                      Added {formatDate(address.added_at)}
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="empty-state">
              <div class="empty-icon">📁</div>
              <h4>No addresses yet</h4>
              <p>Add addresses to this case to start your investigation.</p>
              <button class="btn btn-primary" on:click={() => showAddAddressModal = true}>
                Add First Address
              </button>
            </div>
          {/if}
        </div>
      {:else}
        <div class="empty-state">
          <div class="empty-icon">📋</div>
          <h4>Select a Case</h4>
          <p>Choose a case from the sidebar to view its details and addresses.</p>
        </div>
      {/if}
    </div>
  </div>

  <!-- Create Case Modal -->
  {#if showCreateCaseModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Create New Case</h3>
          <button class="modal-close" on:click={() => showCreateCaseModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="case-name">Case Name:</label>
            <input 
              id="case-name" 
              type="text" 
              bind:value={newCaseName}
              placeholder="Enter case name..."
            />
          </div>
          <div class="form-group">
            <label for="case-description">Description:</label>
            <textarea 
              id="case-description" 
              bind:value={newCaseDescription}
              placeholder="Describe the investigation..."
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showCreateCaseModal = false}>Cancel</button>
          <button class="btn btn-primary" on:click={handleCreateCase}>Create Case</button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Add Address Modal -->
  {#if showAddAddressModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Add Address to Case</h3>
          <button class="modal-close" on:click={() => showAddAddressModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="address-input">Bitcoin Address:</label>
            <input 
              id="address-input" 
              type="text" 
              bind:value={newAddress}
              placeholder="Enter Bitcoin address..."
            />
          </div>
          <div class="form-group">
            <label for="address-note">Note (optional):</label>
            <textarea 
              id="address-note" 
              bind:value={newNote}
              placeholder="Add a note about this address..."
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showAddAddressModal = false}>Cancel</button>
          <button class="btn btn-primary" on:click={handleAddAddress}>Add Address</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .case-management {
    max-width: 1400px;
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

  /* Case Layout */
  .case-layout {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: 2rem;
    min-height: 600px;
  }

  /* Cases Sidebar */
  .cases-sidebar {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .sidebar-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .sidebar-header h2 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .cases-list {
    max-height: 500px;
    overflow-y: auto;
  }

  .case-item {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e9ecef;
    cursor: pointer;
    transition: background-color 0.2s ease;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .case-item:hover {
    background-color: #f8f9fa;
  }

  .case-item.active {
    background-color: #e3f2fd;
    border-left: 4px solid #007bff;
  }

  .case-info {
    flex: 1;
  }

  .case-info h3 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .case-info p {
    margin: 0 0 0.5rem 0;
    color: #6c757d;
    font-size: 0.85rem;
    line-height: 1.4;
  }

  .case-meta {
    display: flex;
    gap: 1rem;
    font-size: 0.75rem;
    color: #6c757d;
  }

  .delete-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: #dc3545;
    font-size: 1rem;
    padding: 0.25rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
  }

  .delete-btn:hover {
    background-color: #f8d7da;
  }

  .delete-btn.small {
    font-size: 0.8rem;
    padding: 0.1rem 0.3rem;
  }

  /* Case Detail */
  .case-detail {
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .detail-header {
    padding: 1.5rem;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .case-title h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .case-title p {
    margin: 0;
    color: #6c757d;
    font-size: 1rem;
  }

  .case-actions {
    display: flex;
    gap: 1rem;
  }

  .addresses-section {
    padding: 1.5rem;
  }

  .addresses-section h3 {
    margin: 0 0 1.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .addresses-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1rem;
  }

  .address-card {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 1rem;
    border: 1px solid #e9ecef;
  }

  .address-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
  }

  .address-text {
    font-family: monospace;
    background-color: #e9ecef;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .address-details {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .classification-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    width: fit-content;
  }

  .classification-badge.suspicious {
    background-color: #fff3cd;
    color: #856404;
  }

  .classification-badge.normal {
    background-color: #d1edff;
    color: #0c5460;
  }

  .risk-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .risk-badge {
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .risk-score {
    font-size: 0.8rem;
    color: #6c757d;
    font-weight: 500;
  }

  .address-note {
    font-size: 0.85rem;
    color: #495057;
    background-color: white;
    padding: 0.5rem;
    border-radius: 4px;
    border-left: 3px solid #007bff;
  }

  .address-date {
    font-size: 0.75rem;
    color: #6c757d;
  }

  /* Empty State */
  .empty-state {
    text-align: center;
    padding: 3rem;
    color: #6c757d;
  }

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .empty-state h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: #2c3e50;
  }

  .empty-state p {
    margin: 0 0 1.5rem 0;
    font-size: 1rem;
  }

  /* Buttons */
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

  .btn-icon {
    margin-right: 0.5rem;
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

  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-size: 0.9rem;
    font-family: inherit;
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  /* Responsive Design */
  @media (max-width: 1024px) {
    .case-layout {
      grid-template-columns: 1fr;
    }
    
    .cases-sidebar {
      order: 2;
    }
    
    .case-detail {
      order: 1;
    }
  }

  @media (max-width: 768px) {
    .detail-header {
      flex-direction: column;
      gap: 1rem;
      align-items: stretch;
    }

    .case-actions {
      justify-content: center;
    }

    .addresses-grid {
      grid-template-columns: 1fr;
    }
  }
</style> 