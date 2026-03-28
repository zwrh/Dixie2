<script lang="ts">
	import { Arc, Chart, Pie, Svg } from 'layerchart';

	const pieData = [
		{ label: 'Active Clients', value: 42, color: '#7e22ce' },
		{ label: 'Pending', value: 18, color: '#a855f7' },
		{ label: 'Inactive', value: 12, color: '#d8b4fe' },
		{ label: 'New Leads', value: 28, color: '#c084fc' }
	];

	const stats = [
		{ title: 'Total Revenue', value: '$48,250', change: '+12.5%' },
		{ title: 'Active Clients', value: '42', change: '+3.2%' },
		{ title: 'Pending Orders', value: '18', change: '-2.1%' },
		{ title: 'Avg. Response', value: '2.4h', change: '-15.3%' }
	];
</script>

<div class="page">
	<div class="page-header">
		<h1>Dashboard</h1>
		<p class="subtitle">Overview of your workspace</p>
	</div>

	<div class="stats-grid">
		{#each stats as stat}
			<div class="card stat-card">
				<span class="stat-title">{stat.title}</span>
				<span class="stat-value">{stat.value}</span>
				<span class="stat-change" class:positive={stat.change.startsWith('+')} class:negative={stat.change.startsWith('-')}>
					{stat.change}
				</span>
			</div>
		{/each}
	</div>

	<div class="charts-grid">
		<div class="card chart-card">
			<h2>Client Distribution</h2>
			<div class="pie-container">
				<Chart data={pieData} tooltip={{ mode: 'manual' }}>
					<Svg>
						<Pie value="value" innerRadius={50} padAngle={0.03} cornerRadius={4}>
							{#snippet children({ arcs })}
								{#each arcs as arc}
									<Arc data={arc} fill={arc.data.color} />
								{/each}
							{/snippet}
						</Pie>
					</Svg>
				</Chart>
			</div>
			<div class="legend">
				{#each pieData as item}
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

	.stat-change {
		font-size: 0.8rem;
		font-weight: 600;
	}

	.stat-change.positive {
		color: #22c55e;
	}

	.stat-change.negative {
		color: #ef4444;
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

	.pie-container {
		height: 200px;
		margin-bottom: 1rem;
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
