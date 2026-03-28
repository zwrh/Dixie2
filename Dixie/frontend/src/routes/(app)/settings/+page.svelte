<script lang="ts">
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
			const res = await fetch('/api/change-password', {
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
</script>

<div class="page">
	<div class="page-header">
		<h1>Settings</h1>
		<p class="subtitle">Manage your account</p>
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
