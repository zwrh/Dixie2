<script lang="ts">
	import { authFetch } from '$lib/auth';
	import { onRefresh } from '$lib/refresh';

	type HistoryEntry = {
		id: number;
		command: string;
		timestamp: string;
		recipients: string[];
		results: { identifier: string; status: string }[];
	};

	let entries = $state<HistoryEntry[]>([]);
	let loading = $state(true);
	let selectedEntry = $state<HistoryEntry | null>(null);
	let expanded = $state(false);

	const visibleEntries = $derived(expanded ? entries : entries.slice(0, 20));

	async function loadHistory() {
		try {
			const res = await authFetch('/api/command-history');
			if (res.ok) {
				entries = await res.json();
			}
		} catch { /* silent */ }
		loading = false;
	}

	loadHistory();
	onRefresh(loadHistory);
</script>

<div class="page">
	<div class="page-header">
		<h1>Command History</h1>
		<p class="subtitle">Log of all commands sent to clients</p>
	</div>

	{#if loading}
		<div class="card"><div class="placeholder">Loading history...</div></div>
	{:else if entries.length === 0}
		<div class="card"><div class="placeholder">No commands have been sent yet</div></div>
	{:else}
		<div class="card">
			<div class="history-list">
				{#each visibleEntries as entry}
					<button class="history-item" onclick={() => selectedEntry = entry}>
						<div class="history-left">
							<code class="history-cmd">{entry.command}</code>
							<span class="history-time">{entry.timestamp}</span>
						</div>
						<div class="history-right">
							<span class="history-stat sent">{entry.results.filter(r => r.status === 'sent').length} sent</span>
							{#if entry.results.filter(r => r.status === 'failed').length > 0}
								<span class="history-stat failed">{entry.results.filter(r => r.status === 'failed').length} failed</span>
							{/if}
							<span class="history-recipients">{entry.recipients.length} clients</span>
						</div>
					</button>
				{/each}
			</div>
			{#if entries.length > 20 && !expanded}
				<button class="more-link" onclick={() => expanded = true}>
					Show {entries.length - 20} more
				</button>
			{/if}
		</div>
	{/if}
</div>

{#if selectedEntry}
	<div class="modal-backdrop" onclick={() => selectedEntry = null} role="presentation">
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header">
				<h3>Command Details</h3>
				<button class="modal-close" onclick={() => selectedEntry = null}>&times;</button>
			</div>
			<div class="modal-body">
				<div class="detail-row">
					<span class="detail-label">Command</span>
					<code class="detail-value">{selectedEntry.command}</code>
				</div>
				<div class="detail-row">
					<span class="detail-label">Sent</span>
					<span class="detail-value">{selectedEntry.timestamp}</span>
				</div>
				<div class="detail-row">
					<span class="detail-label">Recipients ({selectedEntry.recipients.length})</span>
				</div>
				<div class="recipients-list">
					{#each selectedEntry.results as item}
						<div class="recipient">
							<span class="recipient-dot" style:background-color={item.status === 'sent' ? '#22c55e' : '#ef4444'}></span>
							{item.identifier}
							{#if item.status === 'failed'}
								<span class="recipient-failed">failed</span>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>
{/if}

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

	.history-list {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.history-item {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		padding: 0.75rem 0.85rem;
		background-color: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 8px;
		cursor: pointer;
		transition: border-color 0.15s ease, background-color 0.15s ease;
		text-align: left;
		width: 100%;
		color: inherit;
		font: inherit;
	}

	.history-item:hover {
		border-color: #1aaf92;
		background-color: var(--color-surface-hover);
	}

	.history-left {
		display: flex;
		flex-direction: column;
		gap: 0.2rem;
		min-width: 0;
	}

	.history-cmd {
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.8rem;
		color: var(--color-text);
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.history-time {
		font-size: 0.7rem;
		color: var(--color-text-muted);
	}

	.history-right {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		flex-shrink: 0;
	}

	.history-stat {
		font-size: 0.7rem;
		font-weight: 600;
		padding: 0.15rem 0.4rem;
		border-radius: 4px;
	}

	.history-stat.sent {
		color: #22c55e;
		background: rgba(34, 197, 94, 0.1);
	}

	.history-stat.failed {
		color: #ef4444;
		background: rgba(239, 68, 68, 0.1);
	}

	.history-recipients {
		font-size: 0.75rem;
		color: #1aaf92;
		font-weight: 500;
	}

	.more-link {
		display: inline-block;
		margin-top: 0.75rem;
		padding: 0;
		background: none;
		border: none;
		color: #1aaf92;
		font-size: 0.8rem;
		font-weight: 500;
		cursor: pointer;
	}

	.more-link:hover {
		text-decoration: underline;
	}

	.modal-backdrop {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 100;
	}

	.modal {
		background-color: var(--color-card-bg);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		width: 100%;
		max-width: 460px;
		box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
	}

	.modal-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 1rem 1.25rem;
		border-bottom: 1px solid var(--color-border);
	}

	.modal-header h3 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		margin: 0;
	}

	.modal-close {
		background: none;
		border: none;
		color: var(--color-text-muted);
		font-size: 1.4rem;
		cursor: pointer;
		padding: 0;
		line-height: 1;
	}

	.modal-close:hover {
		color: var(--color-text);
	}

	.modal-body {
		padding: 1.25rem;
	}

	.detail-row {
		display: flex;
		align-items: baseline;
		gap: 0.75rem;
		margin-bottom: 0.75rem;
	}

	.detail-label {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--color-text-muted);
		flex-shrink: 0;
	}

	.detail-value {
		font-size: 0.85rem;
		color: var(--color-text);
	}

	code.detail-value {
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.8rem;
	}

	.recipients-list {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		max-height: 200px;
		overflow-y: auto;
	}

	.recipient {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.8rem;
		color: var(--color-text);
		padding: 0.35rem 0.5rem;
		background-color: var(--color-surface);
		border-radius: 4px;
	}

	.recipient-dot {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.recipient-failed {
		font-size: 0.7rem;
		color: #ef4444;
		margin-left: auto;
	}
</style>
