<script>
  import { onMount } from 'svelte';
  import { fly, fade } from 'svelte/transition';
  import { casesApi } from '../services/api.js';

  let cases = [];
  let selectedCase = null;
  let showCreateCaseModal = false;
  let showAddAddressModal = false;
  let showEditCaseModal = false;
  let showEditAddressModal = false;
  let showBulkImportModal = false;
  let newCaseName = '';
  let newCaseDescription = '';
  let newCasePriority = 'medium';
  let newCaseTags = '';
  let newAddress = '';
  let newNote = '';
  let newBulkAddresses = '';
  let editingAddress = null;
  let editingCase = null;
  let loading = false;
  let addingAddress = false;
  let error = '';
  let successMessage = '';
  let caseStats = null;
  let filters = {
    search: '',
    status: 'all',
    priority: 'all'
  };

  onMount(async () => {
    console.log('CaseManagement component mounted');
    try {
      await loadCases();
      await loadCaseStats();
    } catch (err) {
      console.error('Error in onMount:', err);
      error = `Failed to initialize: ${err.message || 'Unknown error'}`;
    }
  });

  async function loadCases() {
    try {
      loading = true;
      console.log('Loading cases with filters:', filters);
      const response = await casesApi.list(filters);
      console.log('Cases response:', response);
      cases = response.cases || [];
      console.log('Cases loaded:', cases);
      console.log('Cases array length:', cases.length);
      console.log('First case:', cases[0]);
      
      // Auto-select first case if none is selected and cases exist
      if (cases.length > 0 && !selectedCase) {
        selectedCase = cases[0];
        console.log('Auto-selected first case:', selectedCase);
      }
      
      if (selectedCase && !cases.find(c => c.id === selectedCase.id)) {
        selectedCase = null;
      }
    } catch (err) {
      console.error('Error loading cases:', err);
      error = `Failed to load cases: ${err.message || 'Unknown error'}`;
    } finally {
      loading = false;
    }
  }

  async function loadCaseStats() {
    try {
      const response = await casesApi.getStats();
      caseStats = response;
    } catch (err) {
      console.error('Error loading case stats:', err);
    }
  }

  async function handleCreateCase() {
    if (!newCaseName.trim()) {
      error = 'Case name is required';
      return;
    }

    try {
      console.log('Creating case with data:', { newCaseName, newCaseDescription, newCasePriority, newCaseTags });
      
      const caseData = {
        name: newCaseName.trim(),
        description: newCaseDescription.trim(),
        priority: newCasePriority,
        tags: newCaseTags.trim() ? newCaseTags.split(',').map(t => t.trim()) : []
      };

      console.log('Sending case data:', caseData);
      const newCase = await casesApi.create(caseData);
      console.log('Case created successfully:', newCase);
      
      cases = [newCase, ...cases];
      showCreateCaseModal = false;
      newCaseName = '';
      newCaseDescription = '';
      newCasePriority = 'medium';
      newCaseTags = '';
      successMessage = 'Case created successfully';
      await loadCaseStats();
      
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      console.error('Error creating case:', err);
      error = `Failed to create case: ${err.message || 'Unknown error'}`;
    }
  }

  async function handleUpdateCase() {
    if (!editingCase || !editingCase.name.trim()) {
      error = 'Case name is required';
      return;
    }

    try {
      const caseData = {
        name: editingCase.name.trim(),
        description: editingCase.description.trim(),
        priority: editingCase.priority,
        tags: editingCase.tags || []
      };

      const updatedCase = await casesApi.update(editingCase.id, caseData);
      cases = cases.map(c => c.id === updatedCase.id ? updatedCase : c);
      if (selectedCase && selectedCase.id === updatedCase.id) {
        selectedCase = updatedCase;
      }
      showEditCaseModal = false;
      editingCase = null;
      successMessage = 'Case updated successfully';
      await loadCaseStats();
      
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      error = 'Failed to update case';
      console.error('Error updating case:', err);
    }
  }

  async function handleDeleteCase(caseId) {
    if (!confirm('Are you sure you want to delete this case? This action cannot be undone.')) {
      return;
    }

    try {
      await casesApi.delete(caseId);
      cases = cases.filter(c => c.id !== caseId);
      if (selectedCase && selectedCase.id === caseId) {
        selectedCase = null;
      }
      successMessage = 'Case deleted successfully';
      await loadCaseStats();
      
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      error = 'Failed to delete case';
      console.error('Error deleting case:', err);
    }
  }

  async function handleAddAddress() {
    if (!selectedCase || !newAddress.trim()) {
      error = 'Address is required';
      return;
    }

    try {
      addingAddress = true;
      const addressData = {
        address: newAddress.trim(),
        note: newNote.trim()
      };

      const newAddressData = await casesApi.addAddress(selectedCase.id, addressData);
      
      // Refresh the selected case to get updated addresses
      const updatedCase = await casesApi.get(selectedCase.id);
      selectedCase = updatedCase;
      cases = cases.map(c => c.id === updatedCase.id ? updatedCase : c);
      
      showAddAddressModal = false;
      newAddress = '';
      newNote = '';
      successMessage = 'Address added successfully';
      
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      error = 'Failed to add address';
      console.error('Error adding address:', err);
    } finally {
      addingAddress = false;
    }
  }

  async function handleBulkImport() {
    if (!selectedCase || !newBulkAddresses.trim()) {
      error = 'Addresses are required';
      return;
    }

    try {
      // Parse addresses from text input (one per line)
      const addresses = newBulkAddresses
        .split('\n')
        .map(addr => addr.trim())
        .filter(addr => addr.length > 0);

      if (addresses.length === 0) {
        error = 'No valid addresses found';
        return;
      }

      const result = await casesApi.addAddressesBulk(selectedCase.id, addresses);
      
      // Refresh the selected case to get updated addresses
      const updatedCase = await casesApi.get(selectedCase.id);
      selectedCase = updatedCase;
      cases = cases.map(c => c.id === updatedCase.id ? updatedCase : c);
      
      showBulkImportModal = false;
      newBulkAddresses = '';
      successMessage = `Successfully imported ${result.total_added} addresses. ${result.total_skipped > 0 ? `${result.total_skipped} were skipped.` : ''}`;
      
      setTimeout(() => successMessage = '', 5000);
    } catch (err) {
      error = 'Failed to import addresses';
      console.error('Error importing addresses:', err);
    }
  }

  async function handleRefreshClassification(addressId) {
    try {
      const updatedAddress = await casesApi.refreshAddressClassification(selectedCase.id, addressId);
      
      // Update the address in the selected case
      selectedCase.addresses = selectedCase.addresses.map(a => 
        a.id === updatedAddress.id ? updatedAddress : a
      );
      cases = cases.map(c => c.id === selectedCase.id ? selectedCase : c);
      
      successMessage = 'Address classification refreshed successfully';
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      error = 'Failed to refresh classification';
      console.error('Error refreshing classification:', err);
    }
  }

  async function handleUpdateAddress() {
    if (!editingAddress || !editingAddress.note) {
      return;
    }

    try {
      const addressData = {
        note: editingAddress.note.trim()
      };

      const updatedAddress = await casesApi.updateAddress(
        selectedCase.id, 
        editingAddress.id, 
        addressData
      );
      
      // Update the address in the selected case
      selectedCase.addresses = selectedCase.addresses.map(a => 
        a.id === updatedAddress.id ? updatedAddress : a
      );
      cases = cases.map(c => c.id === selectedCase.id ? selectedCase : c);
      
      showEditAddressModal = false;
      editingAddress = null;
      successMessage = 'Address updated successfully';
      
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      error = 'Failed to update address';
      console.error('Error updating address:', err);
    }
  }

  async function handleDeleteAddress(addressId) {
    if (!confirm('Are you sure you want to remove this address from the case?')) {
      return;
    }

    try {
      await casesApi.removeAddress(selectedCase.id, addressId);
      
      // Refresh the selected case
      const updatedCase = await casesApi.get(selectedCase.id);
      selectedCase = updatedCase;
      cases = cases.map(c => c.id === updatedCase.id ? updatedCase : c);
      
      successMessage = 'Address removed successfully';
      
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      error = 'Failed to remove address';
      console.error('Error removing address:', err);
    }
  }

  async function handleExportCase(caseId) {
    try {
      const response = await casesApi.export(caseId);
      successMessage = 'Case export requested successfully';
      setTimeout(() => successMessage = '', 3000);
    } catch (err) {
      error = 'Failed to export case';
      console.error('Error exporting case:', err);
    }
  }

  function openEditCaseModal(caseItem) {
    editingCase = { ...caseItem };
    showEditCaseModal = true;
  }

  function openEditAddressModal(address) {
    editingAddress = { ...address };
    showEditAddressModal = true;
  }

  let filterTimeout;

  function handleFilterChange() {
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(() => {
      loadCases();
    }, 300);
  }

  function clearError() {
    error = '';
  }

  function clearSuccess() {
    successMessage = '';
  }

  function clearFilters() {
    filters.search = '';
    filters.status = 'all';
    filters.priority = 'all';
    loadCases();
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
    if (typeof date === 'string') {
      date = new Date(date);
    }
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
    <!-- Error and Success Messages -->
    {#if error}
      <div class="message error" in:fly={{ y: -20, duration: 300 }}>
        <span>{error}</span>
        <button class="message-close" on:click={clearError}>×</button>
      </div>
    {/if}
    
    {#if successMessage}
      <div class="message success" in:fly={{ y: -20, duration: 300 }}>
        <span>{successMessage}</span>
        <button class="message-close" on:click={clearSuccess}>×</button>
      </div>
    {/if}
    
    <!-- Case Statistics -->
    {#if caseStats}
      <div class="case-stats-header">
        <div class="stat-item">
          <span class="stat-value">{caseStats.total_cases}</span>
          <span class="stat-label">Total Cases</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{caseStats.active_cases}</span>
          <span class="stat-label">Active</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{caseStats.recent_cases}</span>
          <span class="stat-label">This Week</span>
        </div>
      </div>
    {/if}
    
    <div class="case-layout">
    <!-- Cases List -->
    <div class="cases-sidebar">
      <div class="sidebar-header">
        <h2 class="sidebar-title">Case Management</h2>
        <div class="header-actions">
          <button class="btn btn-primary" on:click={() => showCreateCaseModal = true}>
            New Case
          </button>
        </div>
      </div>
      

      
      <!-- Filters -->
      <div class="case-filters">
        <div class="search-filter">
          <input 
            type="text" 
            placeholder="Search cases..."
            bind:value={filters.search}
            on:input={handleFilterChange}
          />
        </div>
        <div class="filter-row">
          <select bind:value={filters.status} on:change={handleFilterChange}>
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="closed">Closed</option>
            <option value="archived">Archived</option>
          </select>
          <select bind:value={filters.priority} on:change={handleFilterChange}>
            <option value="all">All Priority</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </div>
        <button class="btn btn-secondary small clear-filters" on:click={clearFilters}>
          Clear Filters
        </button>
      </div>
      
      <div class="cases-list">
        {#if loading}
          <div class="loading-state">
            <div class="loading-skeleton">
              <div class="skeleton-line"></div>
              <div class="skeleton-line short"></div>
              <div class="skeleton-line short"></div>
            </div>
            <div class="loading-skeleton">
              <div class="skeleton-line"></div>
              <div class="skeleton-line short"></div>
              <div class="skeleton-line short"></div>
            </div>
          </div>
        {:else if cases.length === 0}
          <div class="empty-state">
            <h4>No cases found</h4>
            <p>Create your first case to start investigating Bitcoin addresses.</p>
            <button class="btn btn-primary" on:click={() => showCreateCaseModal = true}>
              Create First Case
            </button>
          </div>
        {:else}
          {#each cases as caseItem}
            <div 
              class="case-item"
              class:active={selectedCase && selectedCase.id === caseItem.id}
              on:click={() => selectedCase = caseItem}
              on:keydown={(e) => e.key === 'Enter' && (selectedCase = caseItem)}
              role="button"
              tabindex="0"
            >
            <div class="case-main">
              <div class="case-title-row">
                <h3 class="case-name">{caseItem.name}</h3>
                <div class="case-title-actions">
                  <button 
                    class="action-btn edit-btn case-edit-btn"
                    on:click|stopPropagation={() => openEditCaseModal(caseItem)}
                    title="Edit case"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                  <div class="case-badges">
                    <span class="priority-badge {caseItem.priority}">{caseItem.priority}</span>
                    <span class="status-badge {caseItem.status}">{caseItem.status}</span>
                  </div>
                </div>
              </div>
              
              {#if caseItem.description}
                <p class="case-description">{caseItem.description}</p>
              {/if}
              
              <div class="case-footer">
                <div class="case-meta">
                  <span class="address-count">{caseItem.addresses_count || caseItem.addresses?.length || 0} addresses</span>
                  <span class="case-date">{formatDate(caseItem.created_at)}</span>
                </div>
                
                {#if caseItem.tags && caseItem.tags.length > 0}
                  <div class="case-tags">
                    {#each caseItem.tags as tag}
                      <span class="tag">{tag}</span>
                    {/each}
                  </div>
                {/if}
              </div>
            </div>
            </div>
          {/each}
        {/if}
      </div>
    </div>

    <!-- Case Detail -->
    <div class="case-detail">
      {#if selectedCase}
        <div class="detail-header">
          <div class="case-title">
            <div class="case-title-header">
              <h2>{selectedCase.name}</h2>
              <div class="case-badges">
                <span class="priority-badge {selectedCase.priority}">{selectedCase.priority}</span>
                <span class="status-badge {selectedCase.status}">{selectedCase.status}</span>
              </div>
            </div>
            
            {#if selectedCase.description}
              <p class="case-description-detail">{selectedCase.description}</p>
            {:else}
              <p class="case-description-detail no-description">No description provided</p>
            {/if}
            
            {#if selectedCase.tags && selectedCase.tags.length > 0}
              <div class="case-tags">
                {#each selectedCase.tags as tag}
                  <span class="tag">{tag}</span>
                {/each}
              </div>
            {/if}
            
            <div class="case-meta-detail">
              <div class="meta-item">
                <span class="meta-label">Created:</span>
                <span class="meta-value">{formatDate(selectedCase.created_at)}</span>
              </div>
              {#if selectedCase.updated_at && selectedCase.updated_at !== selectedCase.created_at}
                <div class="meta-item">
                  <span class="meta-label">Updated:</span>
                  <span class="meta-value">{formatDate(selectedCase.updated_at)}</span>
                </div>
              {/if}
              <div class="meta-item">
                <span class="meta-label">Addresses:</span>
                <span class="meta-value">{selectedCase.addresses_count || selectedCase.addresses?.length || 0}</span>
              </div>
            </div>
          </div>
          

        </div>

        <div class="addresses-section">
          <div class="addresses-header">
            <h3>Addresses ({selectedCase.addresses_count || selectedCase.addresses?.length || 0})</h3>
            <div class="addresses-actions">
              <button class="btn btn-primary" on:click={() => showAddAddressModal = true}>
                Add Address
              </button>
              <button class="btn btn-secondary" on:click={() => showBulkImportModal = true}>
                Bulk Import
              </button>
            </div>
          </div>
          
          {#if selectedCase.addresses && selectedCase.addresses.length > 0}
            <div class="addresses-list">
              {#each selectedCase.addresses as address}
                <div class="address-item" in:fade={{ delay: address.id * 50 }}>
                  <div class="address-main">
                    <div class="address-title-row">
                      <div class="address-name">
                        {address.address.substring(0, 12)}...{address.address.substring(address.address.length - 8)}
                      </div>
                      <div class="address-actions">
                        <button 
                          class="action-btn refresh-btn"
                          on:click={() => handleRefreshClassification(address.id)}
                          title="Refresh classification"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="23 4 23 10 17 10"></polyline>
                            <polyline points="1 20 1 14 7 14"></polyline>
                            <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
                          </svg>
                        </button>
                        <button 
                          class="action-btn edit-btn"
                          on:click={() => openEditAddressModal(address)}
                          title="Edit address"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                          </svg>
                        </button>
                        <button 
                          class="action-btn delete-btn"
                          on:click={() => handleDeleteAddress(address.id)}
                          title="Remove address"
                        >
                          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3,6 5,6 21,6"></polyline>
                            <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                            <line x1="10" y1="11" x2="10" y2="17"></line>
                            <line x1="14" y1="11" x2="14" y2="17"></line>
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    <div class="address-description">
                      <div class="address-classification">
                        <span class="classification-badge {address.classification?.toLowerCase() || 'unknown'}">
                          {address.classification?.charAt(0).toUpperCase() + address.classification?.slice(1) || 'Unknown'}
                        </span>
                        <span class="confidence-score">
                          {Math.round((address.confidence || 0) * 100)}%
                        </span>
                      </div>
                    </div>
                    
                    <div class="address-footer">
                      <div class="address-meta">
                        <span class="address-date">Added {formatDate(address.added_at)}</span>
                        {#if address.note}
                          <span class="address-note">• {address.note}</span>
                        {/if}
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
            </div>
          {:else}
            <div class="empty-state">
              <div class="empty-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14,2 14,8 20,8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <polyline points="10,9 9,9 8,9"></polyline>
                </svg>
              </div>
              <h4>No addresses yet</h4>
              <p>Add Bitcoin addresses to this case to start your investigation. Each address will be automatically classified and analyzed.</p>
              <div class="empty-actions">
                <button class="btn btn-primary" on:click={() => showAddAddressModal = true}>
                  Add First Address
                </button>
                <button class="btn btn-secondary" on:click={() => showBulkImportModal = true}>
                  Bulk Import
                </button>
              </div>
            </div>
          {/if}
        </div>
      {:else}
        <div class="empty-state">
          <div class="empty-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
          </div>
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
          <div class="form-group">
            <label for="case-priority">Priority:</label>
            <select id="case-priority" bind:value={newCasePriority}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div class="form-group">
            <label for="case-tags">Tags (comma-separated):</label>
            <input 
              id="case-tags" 
              type="text" 
              bind:value={newCaseTags}
              placeholder="Enter tags..."
            />
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
          <button class="btn btn-secondary" on:click={() => showAddAddressModal = false} disabled={addingAddress}>Cancel</button>
          <button class="btn btn-primary" on:click={handleAddAddress} disabled={addingAddress || !newAddress.trim()}>
            {#if addingAddress}
              <svg class="loading-spinner" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="2" x2="12" y2="6"></line>
                <line x1="12" y1="18" x2="12" y2="22"></line>
                <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                <line x1="2" y1="12" x2="6" y2="12"></line>
                <line x1="18" y1="12" x2="22" y2="12"></line>
                <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
              </svg>
              Adding...
            {:else}
              Add Address
            {/if}
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Edit Case Modal -->
  {#if showEditCaseModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Edit Case</h3>
          <button class="modal-close" on:click={() => showEditCaseModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="edit-case-name">Case Name:</label>
            <input 
              id="edit-case-name" 
              type="text" 
              bind:value={editingCase.name}
              placeholder="Enter case name..."
            />
          </div>
          <div class="form-group">
            <label for="edit-case-description">Description:</label>
            <textarea 
              id="edit-case-description" 
              bind:value={editingCase.description}
              placeholder="Describe the investigation..."
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="edit-case-priority">Priority:</label>
            <select id="edit-case-priority" bind:value={editingCase.priority}>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit-case-status">Status:</label>
            <select id="edit-case-status" bind:value={editingCase.status}>
              <option value="active">Active</option>
              <option value="closed">Closed</option>
              <option value="archived">Archived</option>
            </select>
          </div>
          <div class="form-group">
            <label for="edit-case-tags">Tags (comma-separated):</label>
            <input 
              id="edit-case-tags" 
              type="text" 
              value={editingCase.tags ? editingCase.tags.join(', ') : ''}
              on:input={(e) => editingCase.tags = e.target.value.split(',').map(t => t.trim()).filter(t => t)}
              placeholder="Enter tags..."
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-danger" on:click={() => {
            showEditCaseModal = false;
            handleDeleteCase(editingCase.id);
          }}>Delete Case</button>
          <div class="modal-footer-right">
            <button class="btn btn-secondary" on:click={() => showEditCaseModal = false}>Cancel</button>
            <button class="btn btn-primary" on:click={handleUpdateCase}>Update Case</button>
          </div>
        </div>
      </div>
    </div>
  {/if}

  <!-- Edit Address Modal -->
  {#if showEditAddressModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Edit Address</h3>
          <button class="modal-close" on:click={() => showEditAddressModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="edit-address">Bitcoin Address:</label>
            <input 
              id="edit-address" 
              type="text" 
              value={editingAddress.address}
              disabled
            />
          </div>
          <div class="form-group">
            <label for="edit-address-note">Note:</label>
            <textarea 
              id="edit-address-note" 
              bind:value={editingAddress.note}
              placeholder="Add a note about this address..."
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showEditAddressModal = false}>Cancel</button>
          <button class="btn btn-primary" on:click={handleUpdateAddress}>Update Address</button>
        </div>
      </div>
    </div>
  {/if}

  <!-- Bulk Import Modal -->
  {#if showBulkImportModal}
    <div class="modal-overlay" in:fade={{ duration: 200 }}>
      <div class="modal" in:fly={{ y: 20, duration: 300 }}>
        <div class="modal-header">
          <h3>Bulk Import Addresses</h3>
          <button class="modal-close" on:click={() => showBulkImportModal = false}>×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label for="bulk-addresses">Bitcoin Addresses (one per line):</label>
            <textarea 
              id="bulk-addresses" 
              bind:value={newBulkAddresses}
              placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa&#10;3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy&#10;..."
              rows="10"
            ></textarea>
          </div>
          <div class="form-group">
            <p class="help-text">
              Enter Bitcoin addresses, one per line. Each address will be automatically classified and added to the case.
            </p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" on:click={() => showBulkImportModal = false}>Cancel</button>
          <button class="btn btn-primary" on:click={handleBulkImport}>Import Addresses</button>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .case-management {
    max-width: 1400px;
    margin: 0 auto;
    font-family: var(--font-family);
    color: var(--text-primary);
    font-weight: var(--font-weight-normal);
  }

  /* Messages */
  .message {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-md) var(--spacing-lg);
    margin-bottom: var(--spacing-lg);
    border-radius: var(--border-radius-md);
    border: 1px solid;
  }

  .message.error {
    background: #f8d7da;
    color: #721c24;
    border-color: #f5c6cb;
  }

  .message.success {
    background: #d4edda;
    color: #155724;
    border-color: #c3e6cb;
  }

  .message-close {
    background: none;
    border: none;
    font-size: var(--font-size-lg);
    cursor: pointer;
    color: inherit;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .message-close:hover {
    opacity: 0.7;
  }

  /* Loading States */
  .loading-state {
    padding: var(--spacing-lg);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .loading-skeleton {
    background: var(--background-secondary);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-md);
    border: 1px solid var(--border-color);
  }

  .skeleton-line {
    height: 1rem;
    background: var(--background-tertiary);
    border-radius: var(--border-radius-sm);
    margin-bottom: var(--spacing-sm);
    animation: skeleton-loading 1.5s ease-in-out infinite;
  }

  .skeleton-line.short {
    width: 60%;
  }

  @keyframes skeleton-loading {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 0.3; }
  }

  .case-layout {
    display: grid;
    grid-template-columns: 350px 1fr;
    gap: var(--spacing-xl);
    min-height: 600px;
  }

  /* Case Statistics Header */
  .case-stats-header {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
    padding: var(--spacing-lg);
    background: var(--background-secondary);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color);
  }

  /* Cases Sidebar */
  .cases-sidebar {
    background: var(--background-primary);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color);
    overflow: hidden;
  }

  .sidebar-header {
    padding: var(--spacing-xl);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .header-actions {
    display: flex;
    gap: var(--spacing-sm);
    align-items: center;
  }

  .sidebar-title {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    font-family: var(--font-family);
  }

  /* Case Statistics */
  .case-stats {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-md);
  }

  .stat-item {
    text-align: center;
    padding: var(--spacing-md);
    background: var(--background-secondary);
    border-radius: var(--border-radius-md);
    border: 1px solid var(--border-color);
  }

  .stat-value {
    display: block;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-bold);
    color: rgb(0, 136, 255);
    line-height: 1;
  }

  .stat-label {
    display: block;
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin-top: var(--spacing-xs);
  }

  /* Case Filters */
  .case-filters {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
  }

  .search-filter input {
    width: 100%;
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    background: var(--background-primary);
    color: var(--text-primary);
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
  }

  .search-filter input::placeholder {
    color: var(--text-secondary);
  }

  .filter-row {
    display: flex;
    gap: var(--spacing-md);
  }

  .case-filters select {
    flex: 1;
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    background: var(--background-primary);
    color: var(--text-primary);
    font-family: var(--font-family);
    font-size: var(--font-size-sm);
  }

  .clear-filters {
    align-self: flex-end;
    margin-top: var(--spacing-xs);
  }

  .cases-list {
    max-height: calc(100vh - 400px);
    overflow-y: auto;
    padding: var(--spacing-sm);
  }

  .cases-list::-webkit-scrollbar {
    width: 6px;
  }

  .cases-list::-webkit-scrollbar-track {
    background: var(--background-secondary);
    border-radius: 3px;
  }

  .cases-list::-webkit-scrollbar-thumb {
    background: var(--border-color);
    border-radius: 3px;
  }

  .cases-list::-webkit-scrollbar-thumb:hover {
    background: var(--text-secondary);
  }

  .case-item {
    padding: var(--spacing-md);
    border: 1px solid var(--border-color);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    background: var(--background-primary);
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    border-radius: var(--border-radius-md);
  }

  .case-item:hover {
    background-color: var(--background-secondary);
    border-color: rgb(0, 136, 255);
  }

  .case-item.active {
    background-color: var(--background-tertiary);
    border-color: rgb(0, 136, 255);
    border-left: 4px solid rgb(0, 136, 255);
  }

  .case-main {
    flex: 1;
    min-width: 0;
  }

  .case-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
    gap: var(--spacing-sm);
  }

  .case-title-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }

  .case-edit-btn {
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .case-item:hover .case-edit-btn {
    opacity: 1;
  }

  .case-name {
    margin: 0;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    flex: 1;
    min-width: 0;
    line-height: 1.2;
  }

  .case-badges {
    display: flex;
    gap: var(--spacing-xs);
    flex-shrink: 0;
  }

  .priority-badge,
  .status-badge {
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
  }

  .priority-badge.low {
    background: rgba(40, 167, 69, 0.1);
    color: rgba(40, 167, 69, 0.8);
    border: 1px solid rgba(40, 167, 69, 0.2);
  }

  .priority-badge.medium {
    background: rgba(255, 193, 7, 0.1);
    color: rgba(255, 193, 7, 0.8);
    border: 1px solid rgba(255, 193, 7, 0.2);
  }

  .priority-badge.high {
    background: rgba(253, 126, 20, 0.1);
    color: rgba(253, 126, 20, 0.8);
    border: 1px solid rgba(253, 126, 20, 0.2);
  }

  .priority-badge.critical {
    background: rgba(220, 53, 69, 0.1);
    color: rgba(220, 53, 69, 0.8);
    border: 1px solid rgba(220, 53, 69, 0.2);
  }

  .status-badge.active {
    background: rgba(40, 167, 69, 0.1);
    color: rgba(40, 167, 69, 0.8);
    border: 1px solid rgba(40, 167, 69, 0.2);
  }

  .status-badge.closed {
    background: rgba(108, 117, 125, 0.1);
    color: rgba(108, 117, 125, 0.8);
    border: 1px solid rgba(108, 117, 125, 0.2);
  }

  .status-badge.archived {
    background: rgba(108, 117, 125, 0.1);
    color: rgba(108, 117, 125, 0.8);
    border: 1px solid rgba(108, 117, 125, 0.2);
  }

  .case-description {
    margin: 0 0 var(--spacing-xs) 0;
    color: var(--text-secondary);
    font-size: var(--font-size-xs);
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

    .case-footer {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .case-meta {
    display: flex;
    gap: var(--spacing-sm);
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
    align-items: center;
  }

  .address-count {
    font-weight: var(--font-weight-medium);
  }

  .case-date {
    color: var(--text-secondary);
  }

  .case-tags {
    display: flex;
    flex-wrap: wrap;
    gap: var(--spacing-xs);
    margin-bottom: var(--spacing-xs);
  }

  .tag {
    background: rgba(0, 136, 255, 0.05);
    color: rgba(0, 136, 255, 0.7);
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
    font-size: 0.7rem;
    border: 1px solid rgba(0, 136, 255, 0.1);
  }

  .btn.small {
    padding: 0.2rem 0.5rem;
    font-size: 0.8rem;
  }

  .action-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0.3rem;
    border-radius: var(--border-radius-sm);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
  }

  .action-btn svg {
    width: 14px;
    height: 14px;
  }

  .edit-btn {
    color: rgb(0, 136, 255);
  }

  .edit-btn:hover {
    background: rgba(0, 136, 255, 0.1);
    color: rgb(0, 136, 255);
  }

  .delete-btn {
    color: #dc3545;
  }

  .delete-btn:hover {
    background: rgba(220, 53, 69, 0.1);
    color: #dc3545;
  }

  .btn-danger {
    background: none;
    border: 1px solid #dc3545;
    color: #dc3545;
    transition: all 0.2s ease;
  }

  .btn-danger:hover {
    background: #dc3545;
    color: white;
  }

  .delete-btn {
    background: none;
    border: 1px solid var(--error-color);
    cursor: pointer;
    color: var(--error-color);
    font-size: var(--font-size-base);
    padding: var(--spacing-xs);
    border-radius: var(--border-radius-sm);
    transition: background 0.2s, color 0.2s;
  }

  .delete-btn:hover {
    background: var(--error-color);
    color: white;
  }

  .delete-btn.small {
    font-size: var(--font-size-sm);
    padding: 0.1rem 0.3rem;
  }

  /* Case Detail */
  .case-detail {
    background: var(--background-primary);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color);
    overflow: hidden;
  }

  .detail-header {
    padding: var(--spacing-lg);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .case-title-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-xs);
  }

  .case-title h2 {
    margin: 0 0 var(--spacing-xs) 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
    flex: 1;
  }

  .case-title .case-badges {
    margin-left: var(--spacing-md);
  }

  .case-title .case-tags {
    margin-bottom: var(--spacing-md);
  }

  .case-meta-detail {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
    margin-top: var(--spacing-sm);
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }

  .meta-label {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    font-weight: var(--font-weight-medium);
    min-width: 80px;
  }

  .meta-value {
    font-size: var(--font-size-sm);
    color: var(--text-primary);
  }

  .case-description-detail {
    margin: var(--spacing-sm) 0;
    color: var(--text-secondary);
    font-size: var(--font-size-base);
    line-height: 1.5;
  }

  .case-description-detail.no-description {
    color: var(--text-tertiary);
    font-style: italic;
  }

  .case-title p {
    margin: 0;
    color: var(--text-secondary);
    font-size: var(--font-size-base);
  }

  .case-actions {
    display: flex;
    gap: var(--spacing-md);
  }

  .addresses-section {
    padding: var(--spacing-xl);
  }

  .addresses-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-lg);
  }

  .addresses-header h3 {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .addresses-actions {
    display: flex;
    gap: var(--spacing-sm);
  }

  .addresses-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .address-item {
    background: var(--background-color);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-md);
    transition: all 0.2s ease;
    cursor: pointer;
  }

  .address-item:hover {
    border-color: var(--accent-color);
    box-shadow: 0 2px 8px rgba(0, 136, 255, 0.1);
  }

  .address-main {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .address-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-sm);
    gap: var(--spacing-sm);
  }

  .address-name {
    font-family: 'Courier New', monospace;
    font-size: var(--font-size-sm);
    color: var(--text-primary);
    font-weight: 500;
    flex: 1;
  }

  .address-actions {
    display: flex;
    gap: var(--spacing-xs);
    opacity: 0;
    transition: opacity 0.2s ease;
  }

  .address-item:hover .address-actions {
    opacity: 1;
  }

  .address-description {
    margin-bottom: var(--spacing-sm);
  }

  .address-classification {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
  }

  .address-footer {
    margin-top: auto;
  }

  .address-meta {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
  }

  .address-date {
    color: var(--text-tertiary);
  }

  .address-note {
    color: var(--text-secondary);
  }

  .classification-badge {
    display: inline-block;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius-sm);
    font-size: var(--font-size-xs);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .classification-badge.exchange {
    background: rgba(40, 167, 69, 0.1);
    color: rgba(40, 167, 69, 0.8);
    border: 1px solid rgba(40, 167, 69, 0.2);
  }

  .classification-badge.gambling {
    background: rgba(255, 193, 7, 0.1);
    color: rgba(255, 193, 7, 0.8);
    border: 1px solid rgba(255, 193, 7, 0.2);
  }

  .classification-badge.mixer {
    background: rgba(220, 53, 69, 0.1);
    color: rgba(220, 53, 69, 0.8);
    border: 1px solid rgba(220, 53, 69, 0.2);
  }

  .classification-badge.mining {
    background: rgba(108, 117, 125, 0.1);
    color: rgba(108, 117, 125, 0.8);
    border: 1px solid rgba(108, 117, 125, 0.2);
  }

  .classification-badge.unknown {
    background: rgba(108, 117, 125, 0.1);
    color: rgba(108, 117, 125, 0.8);
    border: 1px solid rgba(108, 117, 125, 0.2);
  }

  .confidence-score {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    font-weight: 500;
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
    background: var(--warning-color);
  }

  .risk-badge.high {
    background: var(--error-color);
  }

  .risk-badge.medium {
    background: var(--warning-color);
  }

  .risk-badge.low {
    background: var(--success-color);
  }

  .risk-score {
    font-size: 0.8rem;
    color: var(--text-tertiary);
    font-weight: 500;
  }

  .address-note {
    font-size: 0.85rem;
    color: var(--text-primary);
    background-color: var(--background-primary);
    padding: var(--spacing-sm);
    border-radius: var(--border-radius-sm);
    border-left: 3px solid var(--accent-color);
  }

  .address-date {
    font-size: var(--font-size-xs);
    color: var(--text-tertiary);
  }

  /* Empty State */
  .empty-state {
    text-align: center;
    padding: var(--spacing-2xl);
    color: var(--text-secondary);
  }

  .empty-icon {
    margin-bottom: var(--spacing-md);
    color: var(--text-tertiary);
    display: flex;
    justify-content: center;
  }

  .empty-state h4 {
    margin: 0 0 var(--spacing-xs) 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .empty-state p {
    margin: 0 0 var(--spacing-lg) 0;
    font-size: var(--font-size-base);
    line-height: 1.5;
  }

  .empty-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
  }

  /* Buttons */
  .btn {
    display: inline-flex;
    align-items: center;
    padding: var(--spacing-sm) var(--spacing-lg);
    border: none;
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);
    cursor: pointer;
    transition: all 0.2s;
    font-family: var(--font-family);
  }

  .btn-primary {
    background-color: var(--accent-color);
    color: white;
  }

  .btn-primary:hover {
    background-color: var(--accent-color-hover);
  }

  .btn-secondary {
    background-color: var(--background-secondary);
    color: var(--accent-color);
    border: 1px solid var(--accent-color);
  }

  .btn-secondary:hover {
    background-color: var(--accent-color);
    color: white;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn:disabled:hover {
    background-color: inherit;
    color: inherit;
  }

  .loading-spinner {
    animation: spin 1s linear infinite;
    margin-right: var(--spacing-xs);
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
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
    padding: var(--spacing-md);
  }

  .modal {
    background: var(--background-primary);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-color);
    width: 100%;
    max-width: 500px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-header {
    padding: var(--spacing-xl);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .modal-header h3 {
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .modal-close {
    background: none;
    border: none;
    font-size: var(--font-size-xl);
    cursor: pointer;
    color: var(--text-tertiary);
    padding: 0;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .modal-close:hover {
    color: var(--text-primary);
  }

  .modal-content {
    padding: var(--spacing-xl);
  }

  .modal-footer {
    padding: var(--spacing-xl);
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-md);
  }

  .modal-footer-right {
    display: flex;
    gap: var(--spacing-md);
  }

  /* Form Styles */
  .form-group {
    margin-bottom: var(--spacing-md);
  }

  .form-group label {
    display: block;
    margin-bottom: var(--spacing-xs);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
  }

  .help-text {
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.4;
  }

  .form-group input,
  .form-group textarea {
    width: 100%;
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-sm);
    font-family: var(--font-family);
    background: var(--background-primary);
    color: var(--text-primary);
  }

  .form-group input:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: var(--accent-color);
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
      gap: var(--spacing-md);
      align-items: stretch;
    }

    .case-actions {
      justify-content: center;
    }

    .addresses-grid {
      grid-template-columns: 1fr;
    }
  }

  .sidebar-logo {
    height: 2.5rem;
    width: auto;
    margin-right: var(--spacing-md);
  }
</style> 