<script lang="ts">
	import { scaleBand } from 'd3-scale';
	import { Axis, Bars, Chart, Highlight, Svg, Tooltip } from 'layerchart';

	type Client = {
		name: string;
		company: string;
		email: string;
		status: 'Active' | 'Inactive' | 'Pending';
		revenue: number;
	};

	const clients: Client[] = [
		{ name: 'Ben Dover', company: 'TechVault Inc.', email: 'sarah@techvault.com', status: 'Active', revenue: 12400 },
		{ name: 'JorJor Well', company: 'DataStream LLC', email: 'marcus@datastream.io', status: 'Active', revenue: 9800 },
		{ name: 'Nick Gurh', company: 'CloudNine Solutions', email: 'priya@cloudnine.dev', status: 'Pending', revenue: 6200 },
		{ name: 'Dixie Normus', company: 'Apex Digital', email: 'james@apexdigital.com', status: 'Active', revenue: 15600 },
		{ name: 'Moe Lester', company: 'BrightPath Co.', email: 'elena@brightpath.co', status: 'Inactive', revenue: 3100 },
		{ name: 'Kanye', company: 'NovaTech', email: 'david@novatech.io', status: 'Active', revenue: 11200 },
		{ name: 'Lisa Thompson', company: 'PeakView Labs', email: 'lisa@peakview.com', status: 'Pending', revenue: 7800 },
		{ name: 'Omar Hassan', company: 'SynergyWorks', email: 'omar@synergyworks.net', status: 'Active', revenue: 8900 }
	];

	type ChartData = { name: string; revenue: number };
	const chartData: ChartData[] = clients.map((c) => ({ name: c.name.split(' ')[0], revenue: c.revenue }));

	function statusColor(status: string): string {
		switch (status) {
			case 'Active': return '#22c55e';
			case 'Inactive': return '#ef4444';
			case 'Pending': return '#f59e0b';
			default: return '#6b7280';
		}
	}
</script>

<div class="page">
	<div class="page-header">
		<h1>Management</h1>
		<p class="subtitle">Client overview and revenue breakdown</p>
	</div>

	<div class="card chart-section">
		<h2>Revenue by Client</h2>
		<div class="bar-chart">
			<Chart
				data={chartData}
				x="revenue"
				xDomain={[0, null]}
				xNice
				y="name"
				yScale={scaleBand().padding(0.4)}
				padding={{ left: 60, bottom: 30, right: 16 }}
				tooltip={{ mode: 'band' }}
			>
				<Svg>
					<Axis placement="bottom" grid rule format={(v) => `$${(v / 1000).toFixed(0)}k`} />
					<Axis placement="left" rule />
					<Bars radius={4} class="fill-purple-600" />
					<Highlight area />
				</Svg>
				<Tooltip.Root>
					{#snippet children({ data }: { data: ChartData })}
						<Tooltip.Header>{data.name}</Tooltip.Header>
						<Tooltip.List>
							<Tooltip.Item label="Revenue" value={`$${data.revenue.toLocaleString()}`} />
						</Tooltip.List>
					{/snippet}
				</Tooltip.Root>
			</Chart>
		</div>
	</div>

	<div class="card table-section">
		<h2>All Clients</h2>
		<div class="table-wrapper">
			<table>
				<thead>
					<tr>
						<th>Name</th>
						<th>Company</th>
						<th>Email</th>
						<th>Status</th>
						<th>Revenue</th>
					</tr>
				</thead>
				<tbody>
					{#each clients as client}
						<tr>
							<td class="name-cell">{client.name}</td>
							<td>{client.company}</td>
							<td class="email-cell">{client.email}</td>
							<td>
								<span class="status-badge" style:color={statusColor(client.status)} style:background-color="{statusColor(client.status)}18">
									{client.status}
								</span>
							</td>
							<td class="revenue-cell">${client.revenue.toLocaleString()}</td>
						</tr>
					{/each}
				</tbody>
			</table>
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

	.bar-chart {
		height: 320px;
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

	.email-cell {
		color: var(--color-text-muted);
	}

	.revenue-cell {
		font-weight: 600;
		font-variant-numeric: tabular-nums;
	}

	.status-badge {
		display: inline-block;
		padding: 0.2rem 0.6rem;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 600;
	}
</style>
