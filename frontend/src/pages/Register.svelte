<script>
  import { fly, fade } from 'svelte/transition';

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
      window.location.href = '/login';
    }, 1000);
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      handleRegister();
    }
  }
</script>

<div class="auth-page" in:fly={{ y: 20, duration: 500 }}>
  <div class="auth-container">
    <div class="auth-card" in:fade={{ duration: 300 }}>
      <div class="auth-header">
        <div class="logo">🔍</div>
        <h1>Bitcoin Classifier</h1>
        <p>Create your account</p>
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
          class="btn btn-primary"
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

<style>
  .auth-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
  }

  .auth-container {
    width: 100%;
    max-width: 400px;
  }

  .auth-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    padding: 2rem;
  }

  .auth-header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .logo {
    font-size: 3rem;
    margin-bottom: 1rem;
  }

  .auth-header h1 {
    margin: 0 0 0.5rem 0;
    font-size: 1.8rem;
    font-weight: 700;
    color: #2c3e50;
  }

  .auth-header p {
    margin: 0;
    color: #6c757d;
    font-size: 1rem;
  }

  .auth-form {
    margin-bottom: 2rem;
  }

  .error-message {
    background-color: #f8d7da;
    color: #721c24;
    padding: 0.75rem;
    border-radius: 6px;
    margin-bottom: 1rem;
    font-size: 0.9rem;
  }

  .form-group {
    margin-bottom: 1.5rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #2c3e50;
  }

  .form-group input {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ced4da;
    border-radius: 6px;
    font-size: 1rem;
    font-family: inherit;
    transition: border-color 0.2s ease;
  }

  .form-group input:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  }

  .form-group input:disabled {
    background-color: #f8f9fa;
    cursor: not-allowed;
  }

  .btn {
    width: 100%;
    padding: 0.75rem;
    border: none;
    border-radius: 6px;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
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

  .loading-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top: 2px solid white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  .auth-footer {
    text-align: center;
    color: #6c757d;
    font-size: 0.9rem;
  }

  .auth-footer a {
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
  }

  .auth-footer a:hover {
    text-decoration: underline;
  }
</style> 