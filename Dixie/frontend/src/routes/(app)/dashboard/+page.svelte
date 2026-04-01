<script lang="ts">
	import { authFetch } from '$lib/auth';
	import { onRefresh } from '$lib/refresh';

	// --- Live data from API ---
	let onlineClients = $state(0);
	let totalClients = $state(0);
	let totalCommands = $state(0);
	const offlineClients = $derived(totalClients - onlineClients);
	const activePct = $derived(totalClients > 0 ? Math.round((onlineClients / totalClients) * 100) : 0);

	const radius = 70;
	const circumference = 2 * Math.PI * radius;
	const activeLen = $derived(totalClients > 0 ? (onlineClients / totalClients) * circumference : 0);

	const statusData = $derived([
		{ label: 'Active', value: onlineClients, color: '#22c55e' },
		{ label: 'Unresponsive', value: offlineClients, color: '#ef4444' }
	]);

	const stats = $derived([
		{ title: 'Total Active', value: onlineClients.toString() },
		{ title: 'Total Inactive', value: offlineClients.toString() },
		{ title: 'Total Inventory', value: totalClients.toString() },
		{ title: 'Total Commands Ran', value: totalCommands.toLocaleString() }
	]);

	async function loadStats() {
		try {
			const res = await authFetch('/api/stats');
			if (res.ok) {
				const data = await res.json();
				totalClients = data.total_clients;
				onlineClients = data.online_clients;
				totalCommands = data.total_commands;
			}
		} catch { /* silent */ }
	}

	type HistoryEntry = {
		id: number;
		command: string;
		timestamp: string;
		recipients: string[];
		results: { identifier: string; status: string }[];
	};

	let recentCommands = $state<HistoryEntry[]>([]);

	async function loadRecentCommands() {
		try {
			const res = await authFetch('/api/command-history');
			if (res.ok) {
				const all: HistoryEntry[] = await res.json();
				recentCommands = all.slice(0, 3);
			}
		} catch { /* silent */ }
	}

	loadStats();
	loadRecentCommands();

	const stopRefresh = onRefresh(() => {
		loadStats();
		fetchRecentBeacons();
		loadRecentCommands();
	});

	// --- Recent Beacons ---
	type BeaconEntry = { timestamp: string; ip_address: string; identifier: string | null };

	let recentBeacons = $state<BeaconEntry[]>([]);
	let beaconsLoading = $state(true);

	async function fetchRecentBeacons() {
		beaconsLoading = true;
		try {
			const res = await authFetch('/api/contact-rate?range=day');
			if (res.ok) {
				const rows: BeaconEntry[] = await res.json();
				recentBeacons = rows.slice(0, 10); // Show last 10 beacons
			}
		} catch { /* silent */ }
		beaconsLoading = false;
	}

	fetchRecentBeacons();

	// --- Dixie Pup ---
	type PupAction = 'idle' | 'feed' | 'pet' | 'trick' | 'sleep';
	let pupAction = $state<PupAction>('idle');
	let pupFrame = $state(0);
	let pupTimer: ReturnType<typeof setInterval> | null = null;
	let actionTimer: ReturnType<typeof setTimeout> | null = null;

	const pupFrames: Record<PupAction, string[]> = {
		idle: [
`  / \\__
 (    @\\___
 /         O
/   (_____/
/_____/   U`,
`  / \\__
 (    @\\___
 /         O
/   (_____/
/_____/  U `
		],
		feed: [
`  / \\__
 (    @\\___
  /        O
 /  (___) /
/_____/ U
  nom nom`,
`  / \\__
 (    @\\___
  \\        O
  /  (___)/
/_____/U
 nom nom!`
		],
		pet: [
`  / \\__
 (    ^\\___
 /         O
/   (_____/
/_____/   U
    ~ happy ~`,
`  / \\__
 (    ^\\___
  /        O
 /  (_____/
/_____/   U
   ~ wag wag ~`
		],
		trick: [
`     \\__
  @   __/
  \\  /
   OO
  /  \\
 U    U
  spin!`,
`  / \\__
 (    @\\___
  \\  /    O
   \\/____/
   /     \\
  U       U
  woof!`
		],
		sleep: [
`  / \\__
 (    -\\___
 /         O
/   (_____/   z
/_____/   U  z
            z`,
`  / \\__
 (    -\\___
 /         O
/   (_____/  Z
/_____/   U Z
           Z`
		]
	};

	function startAnimation() {
		if (pupTimer) clearInterval(pupTimer);
		pupFrame = 0;
		pupTimer = setInterval(() => {
			pupFrame = (pupFrame + 1) % 2;
		}, 600);
	}

	startAnimation();

	function doPupAction(action: PupAction) {
		if (actionTimer) clearTimeout(actionTimer);
		pupAction = action;
		pupFrame = 0;
		actionTimer = setTimeout(() => {
			pupAction = 'idle';
		}, 5000);
	}

	const currentFrame = $derived(pupFrames[pupAction][pupFrame] || pupFrames[pupAction][0]);
</script>

<div class="page">
	<div class="page-header">
		<h1>Dashboard</h1>
		<p class="subtitle">Summary of everything</p>
	</div>

	<div class="stats-grid">
		{#each stats as stat}
			<div class="card stat-card">
				<span class="stat-title">{stat.title}</span>
				<span class="stat-value">{stat.value}</span>
			</div>
		{/each}
	</div>

	<div class="charts-grid">
		<div class="card chart-card">
			<h2>System Status</h2>
			<div class="donut-container">
				<svg viewBox="0 0 200 200" class="donut-svg">
					<circle cx="100" cy="100" r={radius} fill="none" stroke="#ef4444" stroke-width="22" />
					<circle cx="100" cy="100" r={radius} fill="none" stroke="#22c55e" stroke-width="22"
						stroke-dasharray="{activeLen} {circumference - activeLen}"
						transform="rotate(-90 100 100)" />
				</svg>
				<div class="donut-center">
					<span class="donut-pct">{activePct}%</span>
					<span class="donut-label">Active</span>
				</div>
			</div>
			<div class="legend">
				{#each statusData as item}
					<div class="legend-item">
						<span class="legend-dot" style:background-color={item.color}></span>
						<span class="legend-label">{item.label}</span>
					</div>
				{/each}
			</div>
		</div>

		<div class="card chart-card">
			<h2>Recent Beacons</h2>
			{#if beaconsLoading}
				<div class="chart-placeholder">Loading...</div>
			{:else if recentBeacons.length === 0}
				<div class="chart-placeholder">No beacons received yet.</div>
			{:else}
				<div class="beacon-list">
					{#each recentBeacons as beacon}
						<div class="beacon-item">
							<span class="beacon-identifier">{beacon.identifier ?? 'Unknown'}</span>
							<span class="beacon-ip">{beacon.ip_address}</span>
							<span class="beacon-time">{beacon.timestamp}</span>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<div class="card chart-card">
			<h2>Recent Activity</h2>
			{#if recentCommands.length === 0}
				<div class="placeholder">
					<span>No commands sent yet</span>
				</div>
			{:else}
				<div class="activity-list">
					{#each recentCommands as entry}
						<div class="activity-item">
							<code class="activity-cmd">{entry.command}</code>
							<div class="activity-meta">
								<span class="activity-clients">{entry.recipients.length} clients</span>
								<span class="activity-time">{entry.timestamp}</span>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>

		<div class="card chart-card pup-card">
			<h2>Dixie</h2>
			<div class="pup-display">
				<pre class="pup-art">{currentFrame}</pre>
			</div>
			<div class="pup-buttons">
				<button class="pup-btn" onclick={() => doPupAction('feed')} disabled={pupAction !== 'idle'}>Feed</button>
				<button class="pup-btn" onclick={() => doPupAction('pet')} disabled={pupAction !== 'idle'}>Pet</button>
				<button class="pup-btn" onclick={() => doPupAction('trick')} disabled={pupAction !== 'idle'}>Trick</button>
				<button class="pup-btn" onclick={() => doPupAction('sleep')} disabled={pupAction !== 'idle'}>Sleep</button>
			</div>
		</div>
	</div>
</div>

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

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.card {
		background-color: var(--color-card-bg);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		padding: 1.25rem;
		transition: background-color 0.2s ease, border-color 0.2s ease;
	}

	.stat-card {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.stat-title {
		font-size: 0.8rem;
		color: var(--color-text-muted);
		font-weight: 500;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.stat-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text);
	}

.charts-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 1rem;
	}

	.chart-card h2 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		margin: 0 0 1rem;
	}

	.chart-placeholder {
		height: 200px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-text-muted);
		font-size: 0.8rem;
		text-align: center;
		padding: 1rem;
	}

	.beacon-list {
		display: flex;
		flex-direction: column;
		gap: 0.4rem;
		max-height: 220px;
		overflow-y: auto;
	}

	.beacon-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.5rem 0.75rem;
		background-color: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		font-size: 0.8rem;
	}

	.beacon-identifier {
		font-weight: 600;
		color: #1aaf92;
		min-width: 80px;
	}

	.beacon-ip {
		color: var(--color-text);
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.75rem;
	}

	.beacon-time {
		margin-left: auto;
		color: var(--color-text-muted);
		font-size: 0.7rem;
	}

	.donut-container {
		height: 200px;
		margin-bottom: 1rem;
		position: relative;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.donut-svg {
		width: 180px;
		height: 180px;
	}

	.donut-center {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		pointer-events: none;
	}

	.donut-pct {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-text);
		line-height: 1;
	}

	.donut-label {
		font-size: 0.7rem;
		color: var(--color-text-muted);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-top: 0.2rem;
	}

	.legend {
		display: flex;
		justify-content: center;
		gap: 1.5rem;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-size: 0.8rem;
	}

	.legend-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.legend-label {
		color: var(--color-text-muted);
	}

	.activity-list {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.activity-item {
		padding: 0.6rem 0.75rem;
		background-color: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 6px;
	}

	.activity-cmd {
		display: block;
		font-family: 'SF Mono', 'Fira Code', monospace;
		font-size: 0.8rem;
		color: var(--color-text);
		margin-bottom: 0.3rem;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}

	.activity-meta {
		display: flex;
		gap: 0.75rem;
		font-size: 0.7rem;
		color: var(--color-text-muted);
	}

	.activity-clients {
		color: #1aaf92;
		font-weight: 500;
	}

	.pup-card {
		display: flex;
		flex-direction: column;
	}

	.pup-display {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 140px;
	}

	.pup-art {
		font-family: 'SF Mono', 'Fira Code', 'Courier New', monospace;
		font-size: 0.7rem;
		line-height: 1.3;
		color: #1aaf92;
		margin: 0;
		white-space: pre;
		text-align: center;
	}

	.pup-buttons {
		display: flex;
		gap: 0.4rem;
	}

	.pup-btn {
		flex: 1;
		padding: 0.4rem 0;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: 6px;
		color: var(--color-text);
		font-size: 0.7rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.15s ease;
	}

	.pup-btn:hover:not(:disabled) {
		border-color: #1aaf92;
		color: #1aaf92;
	}

	.pup-btn:disabled {
		opacity: 0.35;
		cursor: not-allowed;
	}

	.placeholder {
		height: 200px;
		display: flex;
		align-items: center;
		justify-content: center;
		border: 2px dashed var(--color-border);
		border-radius: 8px;
		color: var(--color-text-muted);
		font-size: 0.875rem;
	}

	@media (max-width: 768px) {
		.stats-grid {
			grid-template-columns: repeat(2, 1fr);
		}

		.charts-grid {
			grid-template-columns: 1fr;
		}
	}
</style>
