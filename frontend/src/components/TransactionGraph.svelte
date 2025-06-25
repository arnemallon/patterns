<script>
  import { onMount, onDestroy, createEventDispatcher, tick } from 'svelte';
  import { apiService } from '../services/api.js';
  import { fly, fade } from 'svelte/transition';
  
  export let address = '';
  export let visible = false;
  
  let graphWrapper;
  let networkContainer;
  let network = null;
  let loading = false;
  let error = null;
  let graphData = null;
  let visNetworkLib = null;
  let observer;
  
  const dispatch = createEventDispatcher();
  
  onMount(async () => {
    // Pre-load the vis-network library
    if (typeof window !== 'undefined') {
      try {
        console.log('Loading vis-network libraries...');
        
        // Import the libraries
        const visNetwork = await import('vis-network');
        const visData = await import('vis-data');
        
        console.log('Vis-network imported successfully:', visNetwork);
        console.log('Vis-data imported successfully:', visData);
        
        visNetworkLib = {
          Network: visNetwork.Network,
          DataSet: visData.DataSet,
        };

        observer = new ResizeObserver(debounce(() => {
          if (network) {
            network.fit({ animation: { duration: 300, easingFunction: 'easeOutQuad' } });
          }
        }, 150));

        console.log('Vis-network libraries loaded successfully');

      } catch (e) {
        console.error('Failed to pre-load vis-network:', e);
        error = `Failed to load graph visualization library: ${e.message}`;
      }
    }
  });
  
  onDestroy(() => {
    if (network) {
      network.destroy();
    }
    if (observer) {
      observer.disconnect();
    }
  });

  async function initializeGraph() {
    console.log('Initializing graph for address:', address);
    console.log('VisNetworkLib available:', !!visNetworkLib);
    
    if (!address || !visNetworkLib) {
      console.log('Missing address or visNetworkLib, returning');
      return;
    }

    loading = true;
    error = null;
    graphData = null;

    try {
      console.log('Fetching graph data from API...');
      graphData = await apiService.getTransactionGraph(address);
      console.log('Graph data received:', graphData);
      
      // After data is loaded, wait for Svelte to render the container div
      await tick();
      console.log('Container rendered, creating network...');

      if (graphData && graphData.nodes && graphData.nodes.length > 0) {
        createNetwork(visNetworkLib.Network, visNetworkLib.DataSet);
      } else {
        console.log('No graph data or nodes available');
      }
    } catch (err) {
      console.error('Failed to load graph data:', err);
      
      // Handle specific error types
      if (err.message && err.message.includes('rate limit')) {
        error = {
          message: 'API Rate Limit Reached',
          details: 'BlockCypher API rate limit exceeded. Please wait a few minutes and try again, or try a different address.'
        };
      } else if (err.message && err.message.includes('Network Error')) {
        error = {
          message: 'Network Error',
          details: 'Could not connect to the server. Please check your connection and try again.'
        };
      } else {
        error = {
          message: err.message || 'Failed to load transaction data',
          details: err.details || 'An unexpected error occurred while loading the graph.'
        };
      }
    } finally {
      loading = false;
    }
  }
  
  function createNetwork(Network, DataSet) {
    console.log('Creating network with container:', !!networkContainer);
    if (!networkContainer) {
      console.log('No network container available');
      return;
    }
    
    if (network) {
      console.log('Destroying existing network');
      network.destroy();
    }
    
    console.log('Creating DataSets...');
    const nodes = new DataSet(graphData.nodes.map(node => ({ ...node })));
    const edges = new DataSet(graphData.edges.map(edge => ({ ...edge })));
    
    console.log('Nodes count:', nodes.length);
    console.log('Edges count:', edges.length);
    
    const options = {
      physics: {
        barnesHut: {
          gravitationalConstant: -8000,
          springConstant: 0.08,
          springLength: 250,
          avoidOverlap: 0.1
        },
        stabilization: { iterations: 150 }
      },
      interaction: { hover: true, tooltipDelay: 200 },
      layout: { improvedLayout: true }
    };
    
    console.log('Creating Network instance...');
    network = new Network(networkContainer, { nodes, edges }, options);
    console.log('Network created successfully');
    
    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        const node = nodes.get(params.nodes[0]);
        if (node && node.address) dispatch('nodeClick', { address: node.address });
      }
    });
  }

  function debounce(func, timeout = 100){
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => { func.apply(this, args); }, timeout);
    };
  }

  // This reactive statement is still useful for resizing the window
  $: if (graphWrapper && observer) {
    if (visible) {
      observer.observe(graphWrapper);
    } else {
      observer.disconnect();
    }
  }
  
  function closeGraph() { dispatch('close'); }
  function refreshGraph() { initializeGraph(); }
</script>

{#if visible}
  <div class="graph-overlay" in:fade={{ duration: 200 }} on:introend={initializeGraph}>
    <div class="graph-container" bind:this={graphWrapper}>
      <div class="graph-header">
        <h3>Transaction Graph for {address ? `${address.substring(0, 12)}...` : 'Address'}</h3>
        <div class="graph-controls">
          {#if loading}
            <div class="loading-spinner"></div>
          {:else}
            <button class="refresh-btn" on:click={refreshGraph} title="Refresh graph">↻</button>
          {/if}
          <button class="close-btn" on:click={closeGraph} title="Close graph">×</button>
        </div>
      </div>
      
      <div class="graph-content-wrapper">
        <div class="network-container" bind:this={networkContainer}></div>
        
        {#if error}
          <div class="message-area">
            <div class="error-message">
              <h4>{error.message}</h4>
              {#if error.details}
                <p>{error.details}</p>
              {/if}
            </div>
          </div>
        {:else if loading}
          <div class="message-area">
            <div class="loading-spinner large"></div>
            <p>{error?.details || 'Loading transaction data...'}</p>
          </div>
        {:else if !graphData || !graphData.nodes || graphData.nodes.length === 0}
          <div class="message-area"><p>No transaction data available.</p></div>
        {/if}
      </div>
      
      {#if graphData}
       <div class="graph-info">
           <span>{graphData.nodes.length} addresses</span>
           <span>{graphData.edges.length} transactions</span>
        </div>
      {/if}
    </div>
  </div>
{/if}

<style>
  .graph-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.7);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
    padding: 1rem;
  }
  
  .graph-container {
    background: var(--background-primary);
    border-radius: var(--border-radius-lg);
    box-shadow: none;
    border: 1px solid var(--border-color);
    width: 100%;
    max-width: 95vw;
    height: 90vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  
  .graph-header {
    flex-shrink: 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid var(--border-color);
    background: var(--background-primary);
  }
  
  .graph-header h3 {
    margin: 0;
    font-size: 1.1rem;
    color: var(--text-primary);
    font-family: var(--font-family);
  }
  .graph-controls { display: flex; gap: 0.5rem; align-items: center; }
  .refresh-btn, .close-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: var(--border-radius-md);
    transition: all 0.2s;
    width: 36px;
    height: 36px;
    color: var(--text-secondary);
  }
  .refresh-btn:hover {
    background-color: var(--background-secondary);
    color: var(--accent-color);
    transform: rotate(180deg);
  }
  .close-btn:hover {
    background-color: var(--error-color);
    color: white;
  }
  
  .graph-content-wrapper {
    flex: 1;
    position: relative;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
    min-height: 0;
    background: var(--background-primary);
  }
  
  .network-container {
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    opacity: 0; /* Hide by default */
    transition: opacity 0.3s ease-in-out;
  }
  
  /* Show the container only when there is a valid network instance */
  .network-container:not(:empty) {
    opacity: 1;
  }

  .message-area {
    text-align: center;
    color: var(--text-secondary);
    background: var(--background-primary);
    border-radius: var(--border-radius-md);
    padding: var(--spacing-lg);
  }
  
  .error-message {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: var(--border-radius-md);
    padding: 1.5rem;
    margin: 1rem;
    color: #721c24;
  }
  
  .error-message h4 {
    margin: 0 0 0.5rem 0;
    color: #721c24;
    font-size: 1.1rem;
  }
  
  .error-message p {
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.4;
  }
  
  .graph-info {
    flex-shrink: 0;
    display: flex;
    gap: 1rem;
    padding: 0.75rem 1.5rem;
    background-color: var(--background-secondary);
    border-top: 1px solid var(--border-color);
    font-size: 0.8rem;
    color: var(--text-secondary);
  }
  
  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid transparent;
    border-top-color: var(--accent-color);
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  .loading-spinner.large {
    width: 40px;
    height: 40px;
    border-width: 3px;
    border-top-color: var(--accent-color);
  }
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
</style> 