<script lang="ts">
	import { authFetch } from '$lib/auth';

	// --- Live data from API ---
	let onlineClients = $state(0);
	let totalClients = $state(0);
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
		{ title: 'Total Commands Ran', value: '—' }
	]);

	async function loadStats() {
		try {
			const res = await authFetch('/api/stats');
			if (res.ok) {
				const data = await res.json();
				totalClients = data.total_clients;
				onlineClients = data.online_clients;
			}
		} catch { /* silent */ }
	}

	loadStats();

	// --- Contact Rate Line Chart ---
	type TimeRange = 'day' | 'week' | 'month' | 'year' | 'all';
	type DataPoint = { date: Date; contacts: number };

	let timeRange = $state<TimeRange>('month');
	let contactData = $state<DataPoint[]>([]);
	let chartLoading = $state(true);

	async function fetchContactRate(range: TimeRange) {
		chartLoading = true;
		try {
			const res = await authFetch(`/api/contact-rate?range=${range}`);
			if (res.ok) {
				const rows: { timestamp: string; total: number; responsive: number }[] = await res.json();
				contactData = rows.map(r => ({
					date: new Date(r.timestamp + 'Z'),
					contacts: r.responsive
				}));
			}
		} catch { /* silent */ }
		chartLoading = false;
	}

	function changeRange(range: TimeRange) {
		timeRange = range;
		fetchContactRate(range);
	}

	fetchContactRate('month');

	const chartW = 500;
	const chartH = 180;
	const padL = 40;
	const padR = 10;
	const padT = 10;
	const padB = 24;
	const plotW = chartW - padL - padR;
	const plotH = chartH - padT - padB;

	const yMax = $derived(Math.max(...contactData.map(d => d.contacts), 1));
	const yTicks = $derived(() => {
		const step = Math.ceil(yMax / 4);
		const ticks = [];
		for (let v = 0; v <= yMax; v += step) ticks.push(v);
		if (ticks[ticks.length - 1] < yMax) ticks.push(yMax);
		return ticks;
	});

	const hasData = $derived(contactData.length > 1);

	const linePath = $derived(
		hasData
			? contactData.map((d, i) => {
					const x = padL + (i / (contactData.length - 1)) * plotW;
					const y = padT + plotH - (d.contacts / yMax) * plotH;
					return `${i === 0 ? 'M' : 'L'}${x},${y}`;
				}).join(' ')
			: ''
	);

	const areaPath = $derived(
		linePath +
		` L${padL + plotW},${padT + plotH} L${padL},${padT + plotH} Z`
	);

	function formatLabel(d: Date, range: TimeRange): string {
		switch (range) {
			case 'day': return d.getHours().toString().padStart(2, '0') + ':00';
			case 'week': return d.toLocaleDateString('en', { weekday: 'short' });
			case 'month': return d.getDate().toString();
			case 'year': return d.toLocaleDateString('en', { month: 'short' });
			case 'all': return d.toLocaleDateString('en', { month: 'short', year: '2-digit' });
		}
	}

	const xLabels = $derived(() => {
		const maxLabels = 6;
		const step = Math.max(1, Math.floor(contactData.length / maxLabels));
		return contactData
			.filter((_, i) => i % step === 0 || i === contactData.length - 1)
			.map((d) => ({
				label: formatLabel(d.date, timeRange),
				x: padL + (contactData.indexOf(d) / (contactData.length - 1)) * plotW
			}));
	});

	const rangeOptions: { value: TimeRange; label: string }[] = [
		{ value: 'day', label: 'Day' },
		{ value: 'week', label: 'Week' },
		{ value: 'month', label: 'Month' },
		{ value: 'year', label: 'Year' },
		{ value: 'all', label: 'All Time' }
	];
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
						<span class="legend-value">{item.value}</span>
					</div>
				{/each}
			</div>
		</div>

		<div class="card chart-card">
			<div class="chart-header">
				<h2>Contact Rate</h2>
				<select class="range-select" bind:value={timeRange} onchange={() => changeRange(timeRange)}>
					{#each rangeOptions as opt}
						<option value={opt.value}>{opt.label}</option>
					{/each}
				</select>
			</div>
			<div class="line-chart-container">
				{#if chartLoading}
					<div class="chart-placeholder">Loading...</div>
				{:else if !hasData}
					<div class="chart-placeholder">No contact data yet. Ping cycles will populate this chart.</div>
				{:else}
					<svg viewBox="0 0 {chartW} {chartH}" class="line-chart-svg">
						<!-- Y grid lines & labels -->
						{#each yTicks() as tick}
							{@const y = padT + plotH - (tick / yMax) * plotH}
							<line x1={padL} y1={y} x2={padL + plotW} y2={y} stroke="var(--color-border)" stroke-width="0.5" />
							<text x={padL - 6} y={y + 3} text-anchor="end" fill="var(--color-text-muted)" font-size="9">{tick}</text>
						{/each}
						<!-- Area fill -->
						<path d={areaPath} fill="url(#contactGrad)" />
						<!-- Line -->
						<path d={linePath} fill="none" stroke="#a855f7" stroke-width="2" stroke-linejoin="round" />
						<!-- Data dots -->
						{#each contactData as d, i}
							{@const x = padL + (i / (contactData.length - 1)) * plotW}
							{@const y = padT + plotH - (d.contacts / yMax) * plotH}
							<circle cx={x} cy={y} r="2.5" fill="#a855f7" />
						{/each}
						<!-- X labels -->
						{#each xLabels() as lbl}
							<text x={lbl.x} y={chartH - 4} text-anchor="middle" fill="var(--color-text-muted)" font-size="9">{lbl.label}</text>
						{/each}
						<!-- Gradient def -->
						<defs>
							<linearGradient id="contactGrad" x1="0" y1="0" x2="0" y2="1">
								<stop offset="0%" stop-color="#a855f7" stop-opacity="0.25" />
								<stop offset="100%" stop-color="#a855f7" stop-opacity="0.02" />
							</linearGradient>
						</defs>
					</svg>
				{/if}
			</div>
		</div>

		<div class="card chart-card">
			<h2>Recent Activity</h2>
			<div class="placeholder">
				<span>Activity feed coming soon</span>
			</div>
		</div>

		<div class="card chart-card">
			<h2>Performance</h2>
			<div class="placeholder">
				<span>Metrics coming soon</span>
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

	.chart-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 1rem;
	}

	.chart-header h2 {
		margin: 0;
	}

	.range-select {
		padding: 0.35rem 0.6rem;
		border: 1px solid var(--color-border);
		border-radius: 6px;
		background-color: var(--color-surface);
		color: var(--color-text);
		font-size: 0.75rem;
		font-weight: 500;
		cursor: pointer;
		appearance: auto;
	}

	.range-select:focus {
		outline: none;
		border-color: #a855f7;
	}

	.line-chart-container {
		height: 200px;
	}

	.line-chart-svg {
		width: 100%;
		height: 100%;
	}

	.chart-placeholder {
		height: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-text-muted);
		font-size: 0.8rem;
		text-align: center;
		padding: 1rem;
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
		flex-direction: column;
		gap: 0.5rem;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-size: 0.8rem;
	}

	.legend-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.legend-label {
		color: var(--color-text-muted);
		flex: 1;
	}

	.legend-value {
		color: var(--color-text);
		font-weight: 600;
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
