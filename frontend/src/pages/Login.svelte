<script>
  import { fly, fade } from 'svelte/transition';
  import { navigate } from 'svelte-routing';
  import { usersApi, setAuthToken } from '../services/api.js';

  export let handleLogin;

  let username = '';
  let password = '';
  let isLoading = false;
  let error = '';

  async function handleLoginSubmit() {
    if (!username.trim() || !password.trim()) {
      error = 'Please enter both username and password';
      return;
    }

    isLoading = true;
    error = '';

    try {
      // Call the real login API
      const response = await usersApi.login(username, password);
      
      // Set the auth token for future requests
      setAuthToken(response.session_token);
      
      // Call the parent's handleLogin function with user data
      handleLogin({
        username: response.user.username,
        email: response.user.email,
        id: response.user.id,
        role: response.user.role,
        sessionToken: response.session_token
      });
      
      // Redirect to the dashboard
      navigate('/', { replace: true });
    } catch (err) {
      console.error('Login error:', err);
      error = err.message || 'Invalid username or password';
    } finally {
      isLoading = false;
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      handleLoginSubmit();
    }
  }

  function handleForgotPassword() {
    // In a real implementation, this would navigate to a password reset page
    alert('Password reset functionality would be implemented here.');
  }
</script>

<div class="auth-page" in:fly={{ y: 20, duration: 500 }}>
  <div class="auth-center-group">
    <div class="auth-container">
      <div class="auth-card" in:fade={{ duration: 300 }}>
        <div class="auth-header">
          <h1>Sign In</h1>
        </div>

        <form class="auth-form" on:submit|preventDefault={handleLoginSubmit}>
          {#if error}
            <div class="error-message" in:fade>
              {error}
            </div>
          {/if}

          <div class="form-group">
            <label for="username">Username</label>
            <input 
              id="username"
              type="text"
              bind:value={username}
              on:keypress={handleKeyPress}
              placeholder="Enter your username"
              disabled={isLoading}
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input 
              id="password"
              type="password"
              bind:value={password}
              on:keypress={handleKeyPress}
              placeholder="Enter your password"
              disabled={isLoading}
            />
          </div>

          <button 
            type="submit" 
            class="btn btn-primary login-btn"
            disabled={isLoading}
          >
            {#if isLoading}
              <span class="loading-spinner"></span>
              Signing in...
            {:else}
              Sign In
            {/if}
          </button>
        </form>

        <div class="auth-footer">
          <p>Don't have an account? <a href="/register">Sign up</a></p>
        </div>
      </div>
    </div>
    <div class="forgot-password-below-absolute">
      <button type="button" class="forgot-link" on:click={handleForgotPassword}>
        Forgot your password?
      </button>
    </div>
  </div>
</div>

<style>
  .auth-page {
    min-height: 100vh;
    width: 100vw;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--background-secondary);
    padding: 0;
  }

  .auth-container {
    width: 100%;
    max-width: 340px;
    min-width: 340px;
  }

  .auth-card {
    background: var(--background-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-lg);
    padding: var(--spacing-xl);
    width: 340px;
    height: 550px; /* Golden ratio height (340 * 1.618) */
    box-sizing: border-box;
    /* No internal scrolling */
  }

  .auth-header {
    text-align: center;
    margin-bottom: var(--spacing-xl);
    margin-top: 40px;
  }

  .auth-header h1 {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-3xl);
    font-weight: var(--font-weight-semibold);
    color: var(--text-primary);
  }

  .auth-header p {
    margin: 0;
    color: var(--text-secondary);
    font-size: var(--font-size-base);
  }

  .auth-form {
    margin-bottom: var(--spacing-xl);
  }

  .error-message {
    background-color: #fef2f2;
    color: var(--error-color);
    padding: var(--spacing-md);
    border: 1px solid #fecaca;
    border-radius: var(--border-radius-md);
    margin-bottom: var(--spacing-lg);
    font-size: var(--font-size-sm);
  }

  .form-group {
    margin-bottom: var(--spacing-lg);
  }

  .form-group label {
    display: block;
    margin-bottom: var(--spacing-sm);
    font-weight: var(--font-weight-medium);
    color: var(--text-primary);
    font-size: var(--font-size-sm);
  }

  .form-group input {
    width: 100%;
    padding: var(--spacing-md);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-base);
    font-family: var(--font-family);
    background-color: var(--background-primary);
    color: var(--text-primary);
    transition: border-color var(--transition-fast);
  }

  .form-group input:focus {
    outline: none;
    border-color: var(--accent-color);
  }

  .form-group input:disabled {
    background-color: var(--background-secondary);
    cursor: not-allowed;
    opacity: 0.6;
  }

  .login-btn {
    width: 100%;
    padding: var(--spacing-md);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
  }

  .loading-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: var(--spacing-sm);
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .auth-footer {
    text-align: center;
    border-top: 1px solid var(--border-color);
    padding-top: var(--spacing-lg);
  }

  .auth-footer p {
    margin: 0 0 var(--spacing-sm) 0;
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
  }

  .auth-footer a {
    color: var(--accent-color);
    font-weight: var(--font-weight-medium);
  }

  .auth-center-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100vw;
    height: 100vh;
    position: relative;
  }

  .forgot-password-below-absolute {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    top: calc(50% + 304px); /* 320px is card height/2 + margin */
    width: 340px;
    display: flex;
    justify-content: center;
  }

  .forgot-link {
    background: none;
    border: none;
    padding: 0;
    font-size: var(--font-size-sm);
    color: var(--text-secondary);
    text-decoration: underline;
    cursor: pointer;
    font-family: var(--font-family);
    transition: color var(--transition-fast);
  }

  .forgot-link:hover {
    color: var(--text-primary);
  }
</style> 