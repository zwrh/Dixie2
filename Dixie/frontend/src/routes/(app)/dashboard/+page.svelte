<script lang="ts">
	const statusData = [
		{ label: 'Active', value: 74, color: '#22c55e' },
		{ label: 'Unresponsive', value: 26, color: '#ef4444' }
	];

	const totalOps = statusData.reduce((sum, d) => sum + d.value, 0);
	const activePct = Math.round((statusData[0].value / totalOps) * 100);

	const radius = 70;
	const circumference = 2 * Math.PI * radius;
	const activeLen = (statusData[0].value / totalOps) * circumference;

	const stats = [
		{ title: 'Total Active', value: '74' },
		{ title: 'Total Inactive', value: '26' },
		{ title: 'Total Inventory', value: '100' },
		{ title: 'Total Commands Ran', value: '1,847' }
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
			<h2>Revenue Trend</h2>
			<div class="placeholder">
				<span>Chart coming soon</span>
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
