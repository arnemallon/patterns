<script>
  import { fly, fade } from 'svelte/transition';
  import { navigate } from 'svelte-routing';

  let username = '';
  let email = '';
  let password = '';
  let confirmPassword = '';
  let isLoading = false;
  let error = '';

  function handleRegister() {
    if (!username.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()) {
      error = 'Please fill in all fields';
      return;
    }

    if (password !== confirmPassword) {
      error = 'Passwords do not match';
      return;
    }

    if (password.length < 8) {
      error = 'Password must be at least 8 characters long';
      return;
    }

    isLoading = true;
    error = '';

    // Simulate registration
    setTimeout(() => {
      console.log('Registration successful');
      // In real implementation, this would redirect to login
      navigate('/login', { replace: true });
    }, 1000);
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      handleRegister();
    }
  }
</script>

<div class="auth-page" in:fly={{ y: 20, duration: 500 }}>
  <div class="auth-center-group">
    <div class="auth-container">
      <div class="auth-card" in:fade={{ duration: 300 }}>
        <div class="auth-header">
          <h1>Sign Up</h1>
        </div>

        <form class="auth-form" on:submit|preventDefault={handleRegister}>
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
              placeholder="Choose a username"
              disabled={isLoading}
            />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input 
              id="email"
              type="email"
              bind:value={email}
              on:keypress={handleKeyPress}
              placeholder="Enter your email"
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
              placeholder="Create a password"
              disabled={isLoading}
            />
          </div>

          <div class="form-group">
            <label for="confirm-password">Confirm Password</label>
            <input 
              id="confirm-password"
              type="password"
              bind:value={confirmPassword}
              on:keypress={handleKeyPress}
              placeholder="Confirm your password"
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
              Creating account...
            {:else}
              Create Account
            {/if}
          </button>
        </form>

        <div class="auth-footer">
          <p>Already have an account? <a href="/login">Sign in</a></p>
        </div>
      </div>
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

  .auth-center-group {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-lg);
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
    height: 650px; /* Adjusted for additional form fields */
    box-sizing: border-box;
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
    color: var(--text-tertiary);
    cursor: not-allowed;
  }

  .btn {
    width: 100%;
    padding: var(--spacing-md);
    border: none;
    border-radius: var(--border-radius-md);
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-medium);
    font-family: var(--font-family);
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: var(--spacing-sm);
  }

  .btn-primary {
    background-color: var(--accent-color);
    color: white;
  }

  .btn-primary:hover:not(:disabled) {
    background-color: var(--accent-hover);
  }

  .btn-primary:disabled {
    background-color: var(--border-color);
    color: var(--text-tertiary);
    cursor: not-allowed;
  }

  .login-btn {
    margin-top: var(--spacing-lg);
  }

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .auth-footer {
    text-align: center;
    margin-top: auto;
  }

  .auth-footer p {
    margin: 0;
    color: var(--text-secondary);
    font-size: var(--font-size-sm);
  }

  .auth-footer a {
    color: var(--accent-color);
    text-decoration: none;
    font-weight: var(--font-weight-medium);
  }

  .auth-footer a:hover {
    text-decoration: underline;
  }

  @media (max-width: 480px) {
    .auth-container {
      max-width: 100%;
      min-width: auto;
      padding: 0 var(--spacing-md);
    }

    .auth-card {
      width: 100%;
      height: auto;
      min-height: 600px;
    }
  }
</style> 