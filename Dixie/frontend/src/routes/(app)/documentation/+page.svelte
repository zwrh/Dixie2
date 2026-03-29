<script lang="ts">
	const sections = [
		{
			title: 'Prerequisites',
			description: 'What you need before deploying Dixie2.',
			steps: [
				'Python 3.10+ and Node.js 18+ installed on the C2 server',
				'Network access to target machines on their configured ports',
				'Rootkit implant deployed on each target machine',
				'A .env file with your JWT_SECRET for API authentication'
			]
		},
		{
			title: 'Server Setup',
			description: 'Getting the Dixie2 backend and frontend running.',
			steps: [
				'Clone the repository and cd into Dixie/backend',
				'Create a Python venv: python3 -m venv venv && source venv/bin/activate',
				'Install dependencies: pip install -r requirements.txt',
				'Create .env with JWT_SECRET=<your-secret>',
				'Start the backend: python3 app.py (runs on port 5001)',
				'In a second terminal, cd into Dixie/frontend and run npm install && npm run dev'
			]
		},
		{
			title: 'Registering Clients',
			description: 'Adding target machines to the database so Dixie2 can reach them.',
			steps: [
				'Navigate to Management and click "+ Add Client"',
				'Enter a unique identifier (callsign) for the machine',
				'Select the OS type (Windows or Linux)',
				'Provide the IP address and port where the implant is listening',
				'The health check scheduler will begin pinging the client automatically'
			]
		},
		{
			title: 'Sending Commands',
			description: 'Dispatching kernel-level commands to active clients via the rootkit.',
			steps: [
				'Go to Management and type your command in the Send Command field',
				'Press Enter to open the target selection popup',
				'Only responsive (online) clients are listed — select individually or use Select All',
				'Click "Send to N clients" to dispatch the command to each selected implant',
				'Results (sent/failed per client) are logged in Command History'
			]
		},
		{
			title: 'Health Monitoring',
			description: 'How Dixie2 tracks which clients are alive.',
			steps: [
				'The backend runs a ping scheduler at a configurable interval (Settings > Health Check Interval)',
				'Each cycle sends ICMP pings to all registered client IPs',
				'Responsive clients are marked online with a last_seen timestamp',
				'Non-responsive clients are flagged offline in the dashboard and client table',
				'The Contact Rate chart on the dashboard shows responsive client count over time'
			]
		},
		{
			title: 'Dashboard Overview',
			description: 'Understanding the metrics displayed on the main dashboard.',
			steps: [
				'Total Active / Inactive / Inventory cards show live client counts from the database',
				'Total Commands Ran counts all commands ever dispatched',
				'System Status donut shows the active vs unresponsive ratio',
				'Contact Rate line chart plots responsive clients over a selectable time range',
				'Recent Activity shows the 3 most recent commands sent'
			]
		},
		{
			title: 'Settings & Security',
			description: 'Configuring Dixie2 and securing your access.',
			steps: [
				'Change your admin password under Settings > Change Password',
				'Adjust the health check ping interval under Settings > Configuration',
				'JWT tokens expire after 24 hours — re-login to get a fresh token',
				'Never expose the .env file or JWT_SECRET in version control'
			]
		}
	];
</script>

<div class="page">
	<div class="page-header">
		<h1>Documentation</h1>
		<p class="subtitle">Setup, usage, and operational reference</p>
	</div>

	<div class="intro-card card">
		<div class="intro-badge">v2.0</div>
		<h2>Dixie2 Command & Control</h2>
		<p>
			Dixie2 is a C2 dashboard for managing rootkit implants across target machines.
			Register clients by IP, monitor their health via automated ICMP pings, and
			dispatch kernel-level commands to selected active hosts. This guide covers
			deployment, client registration, command dispatch, and monitoring.
		</p>
	</div>

	<div class="sections">
		{#each sections as section, i}
			<div class="card section-card">
				<div class="section-number">{String(i + 1).padStart(2, '0')}</div>
				<div class="section-content">
					<h3>{section.title}</h3>
					<p class="section-desc">{section.description}</p>
					<ol class="step-list">
						{#each section.steps as step}
							<li>{step}</li>
						{/each}
					</ol>
				</div>
			</div>
		{/each}
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
		transition: background-color 0.2s ease, border-color 0.2s ease;
	}

	.intro-card {
		margin-bottom: 1.5rem;
		border-left: 4px solid #0e7161;
	}

	.intro-badge {
		display: inline-block;
		padding: 0.2rem 0.6rem;
		background: rgba(26, 175, 146, 0.1);
		color: #1aaf92;
		border-radius: 20px;
		font-size: 0.75rem;
		font-weight: 600;
		margin-bottom: 0.75rem;
	}

	.intro-card h2 {
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--color-text);
		margin: 0 0 0.5rem;
	}

	.intro-card p {
		color: var(--color-text-muted);
		font-size: 0.875rem;
		line-height: 1.6;
		margin: 0;
	}

	.sections {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.section-card {
		display: flex;
		gap: 1.25rem;
	}

	.section-number {
		font-size: 1.5rem;
		font-weight: 800;
		color: #0e7161;
		opacity: 0.3;
		line-height: 1;
		padding-top: 0.15rem;
		flex-shrink: 0;
		width: 2rem;
	}

	.section-content {
		flex: 1;
	}

	.section-content h3 {
		font-size: 1rem;
		font-weight: 600;
		color: var(--color-text);
		margin: 0 0 0.25rem;
	}

	.section-desc {
		color: var(--color-text-muted);
		font-size: 0.85rem;
		margin: 0 0 0.75rem;
		line-height: 1.5;
	}

	.step-list {
		margin: 0;
		padding-left: 1.25rem;
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
	}

	.step-list li {
		font-size: 0.85rem;
		color: var(--color-text-muted);
		line-height: 1.5;
	}

	.step-list li::marker {
		color: #1aaf92;
		font-weight: 600;
	}
</style>
