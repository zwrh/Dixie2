<script lang="ts">
	import { goto } from '$app/navigation';
	import { theme } from '$lib/stores/theme.svelte';
	import { setToken } from '$lib/auth';

	let username = $state('');
	let password = $state('');
	let error = $state('');
	let loading = $state(false);

	async function handleLogin(e: Event) {
		e.preventDefault();
		error = '';
		loading = true;

		try {
			const res = await fetch('/api/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ username, password })
			});

			const data = await res.json();

			if (res.ok) {
				setToken(data.token);
				goto('/dashboard');
			} else {
				error = data.error || 'Login failed.';
			}
		} catch {
			error = 'Unable to connect to server.';
		} finally {
			loading = false;
		}
	}
</script>

<div class="login-page">
	<div class="login-card">
		<div class="login-header">
			<div class="logo-icon">D</div>
			<h1>Dixie</h1>
			<p>Sign in to your account</p>
		</div>

		<form onsubmit={handleLogin}>
			<div class="field">
				<label for="username">Username</label>
				<input
					id="username"
					type="text"
					bind:value={username}
					placeholder="Enter your username"
					autocomplete="username"
					required
				/>
			</div>

			<div class="field">
				<label for="password">Password</label>
				<input
					id="password"
					type="password"
					bind:value={password}
					placeholder="Enter your password"
					autocomplete="current-password"
					required
				/>
			</div>

			{#if error}
				<div class="error-message">{error}</div>
			{/if}

			<button type="submit" class="btn-login" disabled={loading}>
				{loading ? 'Signing in...' : 'Sign In'}
			</button>
		</form>
	</div>

	<button class="theme-btn" onclick={() => theme.toggle()}>
		{#if theme.dark}
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
				<circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
			</svg>
		{:else}
			<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
				<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
			</svg>
		{/if}
	</button>
</div>

<style>
	.login-page {
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background-color: var(--color-surface-alt);
		position: relative;
	}

	.login-card {
		background-color: var(--color-card-bg);
		border: 1px solid var(--color-border);
		border-radius: 16px;
		padding: 2.5rem;
		width: 100%;
		max-width: 400px;
		box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
	}

	.login-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.logo-icon {
		width: 48px;
		height: 48px;
		background: linear-gradient(135deg, #1aaf92, #0e7161);
		border-radius: 14px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-weight: 700;
		font-size: 1.35rem;
		margin: 0 auto 1rem;
	}

	.login-header h1 {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text);
		margin: 0 0 0.375rem;
	}

	.login-header p {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin: 0;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 1.25rem;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	label {
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--color-text);
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	input {
		padding: 0.7rem 0.875rem;
		border: 1px solid var(--color-border);
		border-radius: 8px;
		background-color: var(--color-surface);
		color: var(--color-text);
		font-size: 0.875rem;
		transition: border-color 0.15s ease;
	}

	input::placeholder {
		color: var(--color-text-muted);
	}

	input:focus {
		outline: none;
		border-color: #1aaf92;
		box-shadow: 0 0 0 3px rgba(26, 175, 146, 0.15);
	}

	.error-message {
		padding: 0.75rem 1rem;
		border-radius: 8px;
		font-size: 0.85rem;
		font-weight: 500;
		background-color: rgba(239, 68, 68, 0.1);
		color: #ef4444;
		border: 1px solid rgba(239, 68, 68, 0.2);
	}

	.btn-login {
		padding: 0.75rem 1.25rem;
		background: linear-gradient(135deg, #1aaf92, #0e7161);
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 0.9rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s ease;
		margin-top: 0.25rem;
	}

	.btn-login:hover {
		opacity: 0.9;
	}

	.btn-login:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.theme-btn {
		position: absolute;
		bottom: 1.5rem;
		right: 1.5rem;
		background: var(--color-card-bg);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		padding: 0.5rem;
		color: var(--color-text-muted);
		cursor: pointer;
		transition: all 0.15s ease;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.theme-btn:hover {
		color: var(--color-text);
		border-color: #1aaf92;
	}
</style>
