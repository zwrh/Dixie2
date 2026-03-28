<script lang="ts">
	import { authFetch } from '$lib/auth';

	type Client = {
		id: number;
		identifier: string;
		system_type: string;
		ip_address: string;
		target_port: number;
		date_added: string;
		last_seen: string | null;
		status: string;
	};

	let clients = $state<Client[]>([]);
	let loading = $state(true);

	async function loadClients() {
		try {
			const res = await authFetch('/api/clients');
			if (res.ok) {
				clients = await res.json();
			}
		} catch { /* silent */ }
		loading = false;
	}

	loadClients();

	function statusColor(status: string): string {
		switch (status) {
			case 'responsive': return '#22c55e';
			case 'non-responsive': return '#ef4444';
			default: return '#6b7280';
		}
	}

	function statusLabel(status: string): string {
		switch (status) {
			case 'responsive': return 'Online';
			case 'non-responsive': return 'Offline';
			default: return status;
		}
	}

	let commandInput = $state('');
	let activeCommand = $state('');
	let commandStatus = $state<'idle' | 'sending' | 'active' | 'error'>('idle');
	let commandError = $state('');

	// Client selection popup
	let showTargetPicker = $state(false);
	let pendingCommand = $state('');
	let selectedIds = $state<Set<number>>(new Set());
	const selectedClients = $derived(clients.filter(c => selectedIds.has(c.id)));
	const allSelected = $derived(clients.length > 0 && selectedIds.size === clients.length);

	function toggleClient(id: number) {
		if (selectedIds.has(id)) {
			selectedIds.delete(id);
		} else {
			selectedIds.add(id);
		}
		selectedIds = new Set(selectedIds);
	}

	function toggleAll() {
		if (allSelected) {
			selectedIds = new Set();
		} else {
			selectedIds = new Set(clients.map(c => c.id));
		}
	}

	function promptTargets() {
		const cmd = commandInput.trim();
		if (!cmd) return;
		pendingCommand = cmd;
		selectedIds = new Set();
		showTargetPicker = true;
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') promptTargets();
	}

	type HistoryEntry = {
		command: string;
		timestamp: string;
		recipients: string[];
		results: { identifier: string; status: string }[];
	};

	let commandHistory = $state<HistoryEntry[]>([]);
	let historyExpanded = $state(false);
	let selectedEntry = $state<HistoryEntry | null>(null);

	const visibleHistory = $derived(historyExpanded ? commandHistory : commandHistory.slice(0, 3));

	async function confirmSend() {
		if (selectedClients.length === 0) return;

		showTargetPicker = false;
		commandStatus = 'sending';
		commandError = '';
		try {
			const res = await authFetch('/api/clients/command', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					identifiers: selectedClients.map(c => c.identifier),
					command: pendingCommand
				})
			});
			const data = await res.json();
			if (res.ok) {
				activeCommand = pendingCommand;
				commandInput = '';
				commandStatus = 'active';
				commandHistory.unshift({
					command: pendingCommand,
					timestamp: new Date().toLocaleString(),
					recipients: selectedClients.map(c => c.identifier),
					results: data.results || []
				});
			} else {
				commandError = data.error || 'Failed to send command.';
				commandStatus = 'error';
			}
		} catch {
			commandError = 'Unable to connect to server.';
			commandStatus = 'error';
		}
	}

	// --- Add Client ---
	let showAddClient = $state(false);
	let newClient = $state({ identifier: '', system_type: '', ip_address: '', target_port: '' });
	let addError = $state('');
	let addLoading = $state(false);

	async function addClient(e: Event) {
		e.preventDefault();
		addError = '';
		addLoading = true;
		try {
			const res = await authFetch('/api/clients', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(newClient)
			});
			const data = await res.json();
			if (res.ok) {
				showAddClient = false;
				newClient = { identifier: '', system_type: '', ip_address: '', target_port: '' };
				loadClients();
			} else {
				addError = data.error || 'Failed to add client.';
			}
		} catch {
			addError = 'Unable to connect to server.';
		} finally {
			addLoading = false;
		}
	}

	let deleteTarget = $state<Client | null>(null);

	function confirmDelete(client: Client) {
		deleteTarget = client;
	}

	async function executeDelete() {
		if (!deleteTarget) return;
		try {
			const res = await authFetch(`/api/clients/${deleteTarget.id}`, { method: 'DELETE' });
			if (res.ok) {
				loadClients();
			}
		} catch { /* silent */ }
		deleteTarget = null;
	}

	function openDetails(entry: HistoryEntry) {
		selectedEntry = entry;
	}

	function closeDetails() {
		selectedEntry = null;
	}
</script>

<div class="page">
	<div class="page-header">
		<h1>Management</h1>
		<p class="subtitle">Client overview and status monitoring</p>
	</div>

	<div class="card command-section">
		<h2>Send Command</h2>
		<div class="command-row">
			<input
				type="text"
				class="command-input"
				placeholder="Enter command to send to clients..."
				bind:value={commandInput}
				onkeydown={handleKeydown}
				disabled={commandStatus === 'sending'}
			/>
			<button
				class="command-btn"
				onclick={promptTargets}
				disabled={!commandInput.trim() || commandStatus === 'sending'}
			>
				{commandStatus === 'sending' ? 'Sending...' : 'Enter'}
			</button>
		</div>
		{#if activeCommand}
			<div class="active-command">
				<span class="active-dot"></span>
				<span class="active-label">Active:</span>
				<code class="active-value">{activeCommand}</code>
			</div>
		{/if}
		{#if commandError}
			<div class="command-error">{commandError}</div>
		{/if}
	</div>

	{#if commandHistory.length > 0}
		<div class="card history-section">
			<h2>Command History</h2>
			<div class="history-list">
				{#each visibleHistory as entry}
					<button class="history-item" onclick={() => openDetails(entry)}>
						<code class="history-cmd">{entry.command}</code>
						<span class="history-meta">
							<span class="history-recipients">{entry.recipients.length} clients</span>
							<span class="history-time">{entry.timestamp}</span>
						</span>
					</button>
				{/each}
			</div>
			{#if commandHistory.length > 3}
				<button class="more-link" onclick={() => historyExpanded = !historyExpanded}>
					{historyExpanded ? 'Show less' : `Show ${commandHistory.length - 3} more`}
				</button>
			{/if}
		</div>
	{/if}

	{#if selectedEntry}
		<div class="modal-backdrop" onclick={closeDetails} role="presentation">
			<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
				<div class="modal-header">
					<h3>Command Details</h3>
					<button class="modal-close" onclick={closeDetails}>&times;</button>
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
						{#each selectedEntry.results.length > 0 ? selectedEntry.results : selectedEntry.recipients.map(r => ({ identifier: r, status: 'sent' })) as item}
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

	<div class="card table-section">
		<div class="section-header">
			<h2>All Clients</h2>
			<button class="add-client-btn" onclick={() => showAddClient = true}>+ Add Client</button>
		</div>
		{#if loading}
			<div class="placeholder"><span>Loading clients...</span></div>
		{:else if clients.length === 0}
			<div class="placeholder"><span>No clients registered yet</span></div>
		{:else}
			<div class="table-wrapper">
				<table>
					<thead>
						<tr>
							<th>Identifier</th>
							<th>System</th>
							<th>IP Address</th>
							<th>Port</th>
							<th>Status</th>
							<th>Last Seen</th>
							<th></th>
						</tr>
					</thead>
					<tbody>
						{#each clients as client}
							<tr>
								<td class="name-cell">{client.identifier}</td>
								<td>{client.system_type}</td>
								<td class="mono-cell">{client.ip_address}</td>
								<td class="mono-cell">{client.target_port}</td>
								<td>
									<span class="status-badge" style:color={statusColor(client.status)} style:background-color="{statusColor(client.status)}18">
										{statusLabel(client.status)}
									</span>
								</td>
								<td class="muted-cell">{client.last_seen ?? '—'}</td>
								<td class="delete-cell">
									<button class="delete-btn" onclick={() => confirmDelete(client)} title="Remove client">&times;</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>

{#if showTargetPicker}
	<div class="modal-backdrop" onclick={() => showTargetPicker = false} role="presentation">
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header">
				<h3>Select Targets</h3>
				<button class="modal-close" onclick={() => showTargetPicker = false}>&times;</button>
			</div>
			<div class="modal-body">
				<p class="picker-cmd">Command: <code>{pendingCommand}</code></p>
				<div class="picker-actions">
					<button class="select-all-btn" onclick={toggleAll}>
						{allSelected ? 'Deselect All' : 'Select All'}
					</button>
					<span class="target-count">{selectedIds.size} selected</span>
				</div>
				<div class="picker-list">
					{#each clients as client}
						<button
							class="picker-item"
							class:selected={selectedIds.has(client.id)}
							onclick={() => toggleClient(client.id)}
						>
							<span class="picker-check">{selectedIds.has(client.id) ? '✓' : ''}</span>
							<span class="chip-status" style:background-color={statusColor(client.status)}></span>
							<span class="picker-name">{client.identifier}</span>
							<span class="picker-ip">{client.ip_address}</span>
						</button>
					{/each}
				</div>
				<div class="form-actions">
					<button type="button" class="btn-cancel" onclick={() => showTargetPicker = false}>Cancel</button>
					<button type="button" class="btn-submit" onclick={confirmSend} disabled={selectedIds.size === 0}>
						Send to {selectedIds.size} client{selectedIds.size !== 1 ? 's' : ''}
					</button>
				</div>
			</div>
		</div>
	</div>
{/if}

{#if showAddClient}
	<div class="modal-backdrop" onclick={() => showAddClient = false} role="presentation">
		<div class="modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header">
				<h3>Add Client</h3>
				<button class="modal-close" onclick={() => showAddClient = false}>&times;</button>
			</div>
			<div class="modal-body">
				<form onsubmit={addClient}>
					<div class="form-field">
						<label for="ac-id">Identifier</label>
						<input id="ac-id" type="text" bind:value={newClient.identifier} placeholder="e.g. SHADOWFANG" required />
					</div>
					<div class="form-field">
						<label for="ac-sys">System</label>
						<select id="ac-sys" class="form-select" bind:value={newClient.system_type} required>
							<option value="" disabled>Select OS</option>
							<option value="Windows">Windows</option>
							<option value="Linux">Linux</option>
						</select>
					</div>
					<div class="form-field">
						<label for="ac-ip">IP Address</label>
						<input id="ac-ip" type="text" bind:value={newClient.ip_address} placeholder="e.g. 192.168.1.10" required />
					</div>
					<div class="form-field">
						<label for="ac-port">Port</label>
						<input id="ac-port" type="text" inputmode="numeric" pattern="[0-9]*" bind:value={newClient.target_port} placeholder="e.g. 8080" required />
					</div>
					{#if addError}
						<div class="form-error">{addError}</div>
					{/if}
					<div class="form-actions">
						<button type="button" class="btn-cancel" onclick={() => showAddClient = false}>Cancel</button>
						<button type="submit" class="btn-submit" disabled={addLoading}>
							{addLoading ? 'Adding...' : 'Add Client'}
						</button>
					</div>
				</form>
			</div>
		</div>
	</div>
{/if}

{#if deleteTarget}
	<div class="modal-backdrop" onclick={() => deleteTarget = null} role="presentation">
		<div class="modal delete-modal" onclick={(e) => e.stopPropagation()} role="dialog">
			<div class="modal-header">
				<h3>Confirm Deletion</h3>
				<button class="modal-close" onclick={() => deleteTarget = null}>&times;</button>
			</div>
			<div class="modal-body">
				<p class="delete-message">
					Are you sure you want to remove <strong>{deleteTarget.identifier}</strong>?
				</p>
				<p class="delete-details">
					{deleteTarget.system_type} &middot; {deleteTarget.ip_address}:{deleteTarget.target_port}
				</p>
				<p class="delete-warning">This action cannot be undone.</p>
				<div class="form-actions">
					<button type="button" class="btn-cancel" onclick={() => deleteTarget = null}>Cancel</button>
					<button type="button" class="btn-delete" onclick={executeDelete}>Delete Client</button>
				</div>
			</div>
		</div>
	</div>
{/if}

<style>
	.page {
		max-width: 1200px;
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
		margin-bottom: 1.5rem;
		transition: background-color 0.2s ease, border-color 0.2s ease;
	}

	.card h2 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		margin: 0 0 1rem;
	}

	.picker-cmd {
		font-size: 0.85rem;
		color: var(--color-text-muted);
		margin: 0 0 0.75rem;
	}

	.picker-cmd code {
		color: var(--color-text);
		font-family: 'SF Mono', 'Fira Code', monospace;
	}

	.picker-actions {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 0.5rem;
	}

	.select-all-btn {
		background: none;
		border: none;
		color: #1aaf92;
		font-size: 0.8rem;
		font-weight: 600;
		cursor: pointer;
		padding: 0;
	}

	.select-all-btn:hover {
		text-decoration: underline;
	}

	.target-count {
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.picker-list {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		max-height: 260px;
		overflow-y: auto;
		margin-bottom: 1rem;
	}

	.picker-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.6rem;
		border: 1px solid var(--color-border);
		border-radius: 6px;
		background: var(--color-surface);
		cursor: pointer;
		transition: all 0.15s ease;
		text-align: left;
		width: 100%;
		color: inherit;
		font: inherit;
		font-size: 0.8rem;
	}

	.picker-item:hover {
		border-color: #1aaf92;
	}

	.picker-item.selected {
		border-color: #1aaf92;
		background: rgba(26, 175, 146, 0.08);
	}

	.picker-check {
		width: 1rem;
		text-align: center;
		color: #1aaf92;
		font-weight: 700;
		flex-shrink: 0;
	}

	.chip-status {
		width: 6px;
		height: 6px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.picker-name {
		font-weight: 600;
		color: var(--color-text);
		flex: 1;
	}

	.picker-ip {
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.command-row {
		display: flex;
		gap: 0;
	}

	.command-input {
		flex: 1;
		padding: 0.7rem 0.875rem;
		border: 1px solid var(--color-border);
		border-right: none;
		border-radius: 8px 0 0 8px;
		background-color: var(--color-surface);
		color: var(--color-text);
		font-size: 0.875rem;
		font-family: 'SF Mono', 'Fira Code', monospace;
		transition: border-color 0.15s ease;
	}

	.command-input::placeholder {
		color: var(--color-text-muted);
		font-family: inherit;
	}

	.command-input:focus {
		outline: none;
		border-color: #1aaf92;
		box-shadow: 0 0 0 3px rgba(26, 175, 146, 0.15);
	}

	.command-input:disabled {
		opacity: 0.5;
	}

	.command-btn {
		padding: 0.7rem 1.5rem;
		background: linear-gradient(135deg, #1aaf92, #0e7161);
		color: white;
		border: none;
		border-radius: 0 8px 8px 0;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s ease;
		white-space: nowrap;
	}

	.command-btn:hover:not(:disabled) {
		opacity: 0.9;
	}

	.command-btn:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.active-command {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-top: 0.75rem;
		padding: 0.5rem 0.75rem;
		background-color: rgba(34, 197, 94, 0.08);
		border: 1px solid rgba(34, 197, 94, 0.2);
		border-radius: 6px;
		font-size: 0.8rem;
	}

	.active-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background-color: #22c55e;
		flex-shrink: 0;
		animation: pulse 2s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.4; }
	}

	.active-label {
		color: #22c55e;
		font-weight: 600;
	}

	.active-value {
		color: var(--color-text);
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.8rem;
	}

	.command-error {
		margin-top: 0.5rem;
		padding: 0.5rem 0.75rem;
		background-color: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.2);
		border-radius: 6px;
		color: #ef4444;
		font-size: 0.8rem;
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
		padding: 0.6rem 0.75rem;
		background-color: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 6px;
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

	.history-cmd {
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.8rem;
		color: var(--color-text);
	}

	.history-meta {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		font-size: 0.75rem;
		color: var(--color-text-muted);
		flex-shrink: 0;
	}

	.history-recipients {
		color: #1aaf92;
		font-weight: 500;
	}

	.more-link {
		display: inline-block;
		margin-top: 0.5rem;
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

	.section-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.section-header h2 {
		margin: 0;
	}

	.add-client-btn {
		padding: 0.4rem 0.85rem;
		background: linear-gradient(135deg, #1aaf92, #0e7161);
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 0.8rem;
		font-weight: 600;
		cursor: pointer;
		transition: opacity 0.15s ease;
	}

	.add-client-btn:hover {
		opacity: 0.9;
	}

	.form-field {
		display: flex;
		flex-direction: column;
		gap: 0.3rem;
		margin-bottom: 1rem;
	}

	.form-field label {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--color-text-muted);
	}

	.form-field input {
		padding: 0.6rem 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: 6px;
		background-color: var(--color-surface);
		color: var(--color-text);
		font-size: 0.85rem;
	}

	.form-field input:focus {
		outline: none;
		border-color: #1aaf92;
		box-shadow: 0 0 0 3px rgba(26, 175, 146, 0.15);
	}

	.form-field input::placeholder {
		color: var(--color-text-muted);
	}

	.form-error {
		padding: 0.5rem 0.75rem;
		background-color: rgba(239, 68, 68, 0.08);
		border: 1px solid rgba(239, 68, 68, 0.2);
		border-radius: 6px;
		color: #ef4444;
		font-size: 0.8rem;
		margin-bottom: 1rem;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 0.5rem;
	}

	.btn-cancel {
		padding: 0.5rem 1rem;
		background: none;
		border: 1px solid var(--color-border);
		border-radius: 6px;
		color: var(--color-text-muted);
		font-size: 0.8rem;
		font-weight: 500;
		cursor: pointer;
	}

	.btn-cancel:hover {
		color: var(--color-text);
		border-color: var(--color-text-muted);
	}

	.btn-submit {
		padding: 0.5rem 1rem;
		background: linear-gradient(135deg, #1aaf92, #0e7161);
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 0.8rem;
		font-weight: 600;
		cursor: pointer;
	}

	.btn-submit:hover:not(:disabled) {
		opacity: 0.9;
	}

	.btn-submit:disabled {
		opacity: 0.4;
		cursor: not-allowed;
	}

	.placeholder {
		height: 120px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px dashed var(--color-border);
		border-radius: 8px;
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	.table-wrapper {
		overflow-x: auto;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
	}

	th {
		text-align: left;
		padding: 0.75rem 1rem;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--color-text-muted);
		border-bottom: 1px solid var(--color-border);
	}

	td {
		padding: 0.75rem 1rem;
		color: var(--color-text);
		border-bottom: 1px solid var(--color-border);
	}

	tbody tr:last-child td {
		border-bottom: none;
	}

	tbody tr:hover {
		background-color: var(--color-surface-hover);
	}

	.name-cell {
		font-weight: 600;
	}

	.mono-cell {
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.8rem;
		color: var(--color-text-muted);
	}

	.delete-cell {
		width: 2rem;
		text-align: center;
	}

	.delete-btn {
		background: none;
		border: none;
		color: #ef4444;
		font-size: 1.2rem;
		font-weight: 700;
		cursor: pointer;
		padding: 0.1rem 0.4rem;
		border-radius: 4px;
		line-height: 1;
		transition: background-color 0.15s ease;
	}

	.delete-btn:hover {
		background-color: rgba(239, 68, 68, 0.1);
	}

	.delete-modal {
		max-width: 400px;
	}

	.delete-message {
		font-size: 0.9rem;
		color: var(--color-text);
		margin: 0 0 0.5rem;
	}

	.delete-details {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		margin: 0 0 0.75rem;
		font-family: 'SF Mono', 'Fira Code', monospace;
	}

	.delete-warning {
		font-size: 0.8rem;
		color: #ef4444;
		margin: 0 0 1.25rem;
	}

	.btn-delete {
		padding: 0.5rem 1rem;
		background-color: #ef4444;
		color: white;
		border: none;
		border-radius: 6px;
		font-size: 0.8rem;
		font-weight: 600;
		cursor: pointer;
	}

	.btn-delete:hover {
		background-color: #dc2626;
	}

	.form-select {
		padding: 0.6rem 0.75rem;
		border: 1px solid var(--color-border);
		border-radius: 6px;
		background-color: var(--color-surface);
		color: var(--color-text);
		font-size: 0.85rem;
		cursor: pointer;
	}

	.form-select:focus {
		outline: none;
		border-color: #1aaf92;
		box-shadow: 0 0 0 3px rgba(26, 175, 146, 0.15);
	}

	.muted-cell {
		color: var(--color-text-muted);
		font-size: 0.8rem;
	}

	.status-badge {
		display: inline-block;
		padding: 0.2rem 0.6rem;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 600;
	}
</style>
