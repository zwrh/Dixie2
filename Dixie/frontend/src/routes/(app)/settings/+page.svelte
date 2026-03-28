<script lang="ts">
	import { authFetch } from '$lib/auth';

	let currentPassword = $state('');
	let newPassword = $state('');
	let confirmPassword = $state('');
	let message = $state('');
	let messageType = $state<'success' | 'error' | ''>('');
	let loading = $state(false);

	async function handleChangePassword(e: Event) {
		e.preventDefault();
		message = '';
		messageType = '';

		if (newPassword !== confirmPassword) {
			message = 'New passwords do not match.';
			messageType = 'error';
			return;
		}

		if (newPassword.length < 8) {
			message = 'Password must be at least 8 characters.';
			messageType = 'error';
			return;
		}

		loading = true;
		try {
			const res = await authFetch('/api/change-password', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					current_password: currentPassword,
					new_password: newPassword
				})
			});

			const data = await res.json();

			if (res.ok) {
				message = 'Password changed successfully.';
				messageType = 'success';
				currentPassword = '';
				newPassword = '';
				confirmPassword = '';
			} else {
				message = data.error || 'Failed to change password.';
				messageType = 'error';
			}
		} catch {
			message = 'Unable to connect to server.';
			messageType = 'error';
		} finally {
			loading = false;
		}
	}

	// --- Configuration Settings ---
	const intervalOptions = [
		{ value: '10', label: '10 seconds' },
		{ value: '30', label: '30 seconds' },
		{ value: '60', label: '1 minute' },
		{ value: '120', label: '2 minutes' },
		{ value: '300', label: '5 minutes' },
		{ value: '600', label: '10 minutes' },
		{ value: '1800', label: '30 minutes' },
		{ value: '3600', label: '1 hour' }
	];

	let pingInterval = $state('30');
	let configMessage = $state('');
	let configSaving = $state(false);

	async function loadSettings() {
		try {
			const res = await authFetch('/api/settings');
			if (res.ok) {
				const data = await res.json();
				if (data.ping_interval) pingInterval = data.ping_interval;
			}
		} catch { /* silent */ }
	}

	async function savePingInterval() {
		configSaving = true;
		configMessage = '';
		try {
			const res = await authFetch('/api/settings', {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ ping_interval: pingInterval })
			});
			if (res.ok) {
				configMessage = 'saved';
				setTimeout(() => configMessage = '', 2000);
			}
		} catch { /* silent */ }
		configSaving = false;
	}

	loadSettings();
</script>

<div class="page">
	<div class="page-header">
		<h1>Settings</h1>
		<p class="subtitle">Manage your account and configuration</p>
	</div>

	<div class="card settings-card">
		<h2>Change Password</h2>
		<p class="description">Update your password to keep your account secure.</p>

		<form onsubmit={handleChangePassword}>
			<div class="field">
				<label for="current">Current Password</label>
				<input
					id="current"
					type="password"
					bind:value={currentPassword}
					placeholder="Enter current password"
					required
				/>
			</div>

			<div class="field">
				<label for="new">New Password</label>
				<input
					id="new"
					type="password"
					bind:value={newPassword}
					placeholder="Enter new password"
					required
				/>
			</div>

			<div class="field">
				<label for="confirm">Confirm New Password</label>
				<input
					id="confirm"
					type="password"
					bind:value={confirmPassword}
					placeholder="Confirm new password"
					required
				/>
			</div>

			{#if message}
				<div class="message" class:success={messageType === 'success'} class:error={messageType === 'error'}>
					{message}
				</div>
			{/if}

			<button type="submit" class="btn-primary" disabled={loading}>
				{loading ? 'Updating...' : 'Update Password'}
			</button>
		</form>
	</div>

	<div class="card settings-card config-card">
		<h2>Configuration</h2>
		<p class="description">Adjust system behavior and monitoring preferences.</p>

		<div class="config-row">
			<div class="config-info">
				<span class="config-label">Health Check Interval</span>
				<span class="config-desc">How often the system pings clients to check their status.</span>
			</div>
			<div class="config-control">
				<select class="config-select" bind:value={pingInterval} onchange={savePingInterval} disabled={configSaving}>
					{#each intervalOptions as opt}
						<option value={opt.value}>{opt.label}</option>
					{/each}
				</select>
				{#if configMessage === 'saved'}
					<span class="config-saved">Saved</span>
				{/if}
			</div>
		</div>
	</div>
</div>

<style>
	.page {
		max-width: 600px;
	}

	.page-header {
		margin-bottom: 2rem;
	}

	.page-header h1 {
		font-size: 1.75rem;
		font-weight: 700;
		color: var(--color-text);
		margin: 0 0 0.25rem;
	}

	.subtitle {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin: 0;
	}

	.card {
		background-color: var(--color-card-bg);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		padding: 1.5rem;
	}

	.config-card {
		margin-top: 1.5rem;
	}

	.config-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
	}

	.config-info {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
	}

	.config-label {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.config-desc {
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}

	.config-control {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-shrink: 0;
	}

	.config-select {
		padding: 0.5rem 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: 8px;
		background-color: var(--color-surface);
		color: var(--color-text);
		font-size: 0.8rem;
		cursor: pointer;
	}

	.config-select:focus {
		outline: none;
		border-color: #a855f7;
	}

	.config-saved {
		font-size: 0.75rem;
		font-weight: 600;
		color: #22c55e;
	}

	.settings-card h2 {
		font-size: 1.125rem;
		font-weight: 600;
		color: var(--color-text);
		margin: 0 0 0.25rem;
	}

	.description {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		margin: 0 0 1.5rem;
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
		padding: 0.625rem 0.875rem;
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
		border-color: #a855f7;
		box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.15);
	}

	.message {
		padding: 0.75rem 1rem;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 500;
	}

	.message.success {
		background-color: rgba(34, 197, 94, 0.1);
		color: #22c55e;
		border: 1px solid rgba(34, 197, 94, 0.2);
	}

	.message.error {
		background-color: rgba(239, 68, 68, 0.1);
		color: #ef4444;
		border: 1px solid rgba(239, 68, 68, 0.2);
	}

	.btn-primary {
		padding: 0.625rem 1.25rem;
		background: linear-gradient(135deg, #a855f7, #7e22ce);
		color: white;
		border: none;
		border-radius: 8px;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s ease;
		align-self: flex-start;
	}

	.btn-primary:hover {
		opacity: 0.9;
	}

	.btn-primary:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>
