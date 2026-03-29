<script lang="ts">
	import { authFetch } from '$lib/auth';
	import { onRefresh } from '$lib/refresh';

	type Client = {
		id: number;
		identifier: string;
		ip_address: string;
		status: string;
		system_type: string;
	};

	let clients = $state<Client[]>([]);
	let loading = $state(true);

	const responsive = $derived(clients.filter((c) => c.status === 'responsive'));
	const unresponsive = $derived(clients.filter((c) => c.status !== 'responsive'));

	async function loadClients() {
		try {
			const res = await authFetch('/api/clients');
			if (res.ok) clients = await res.json();
		} catch {
			/* silent */
		}
		loading = false;
	}

	loadClients();
	onRefresh(loadClients);
</script>

<div class="page">
	<div class="page-header">
		<h1>Terminal</h1>
		<p class="subtitle">Select a client to open an interactive shell session</p>
	</div>

	{#if loading}
		<div class="card"><div class="placeholder">Loading clients...</div></div>
	{:else if clients.length === 0}
		<div class="card"><div class="placeholder">No clients registered</div></div>
	{:else}
		{#if responsive.length > 0}
			<div class="card">
				<h2 class="section-title">Responsive</h2>
				<div class="client-list">
					{#each responsive as client}
						<a href="/terminal/{client.id}" class="client-row">
							<div class="client-info">
								<span class="client-name">{client.identifier}</span>
								<span class="client-ip">{client.ip_address}</span>
							</div>
							<div class="client-right">
								<span class="badge badge-os">{client.system_type}</span>
								<span class="connect-label">Connect &rarr;</span>
							</div>
						</a>
					{/each}
				</div>
			</div>
		{/if}

		{#if unresponsive.length > 0}
			<div class="card" style="margin-top: 1rem;">
				<h2 class="section-title muted">Unresponsive</h2>
				<div class="client-list">
					{#each unresponsive as client}
						<div class="client-row disabled">
							<div class="client-info">
								<span class="client-name">{client.identifier}</span>
								<span class="client-ip">{client.ip_address}</span>
							</div>
							<div class="client-right">
								<span class="badge badge-os">{client.system_type}</span>
								<span class="offline-label">Offline</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.page {
		max-width: 900px;
		margin: 0 auto;
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

	.placeholder {
		height: 120px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	.section-title {
		font-size: 0.8rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: #22c55e;
		margin: 0 0 0.75rem;
	}

	.section-title.muted {
		color: var(--color-text-muted);
	}

	.client-list {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.client-row {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.75rem 0.85rem;
		background-color: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		text-decoration: none;
		color: inherit;
		transition:
			border-color 0.15s ease,
			background-color 0.15s ease;
	}

	a.client-row:hover {
		border-color: #1aaf92;
		background-color: var(--color-surface-hover);
	}

	.client-row.disabled {
		opacity: 0.45;
		cursor: not-allowed;
	}

	.client-info {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
	}

	.client-name {
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--color-text);
	}

	.client-ip {
		font-size: 0.7rem;
		color: var(--color-text-muted);
		font-family: 'SF Mono', 'Fira Code', monospace;
	}

	.client-right {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		flex-shrink: 0;
	}

	.badge {
		font-size: 0.65rem;
		font-weight: 600;
		padding: 0.15rem 0.4rem;
		border-radius: 4px;
	}

	.badge-os {
		color: var(--color-text-muted);
		background: rgba(255, 255, 255, 0.06);
	}

	.connect-label {
		font-size: 0.75rem;
		color: #1aaf92;
		font-weight: 500;
	}

	.offline-label {
		font-size: 0.7rem;
		color: var(--color-text-muted);
	}
</style>
