<script lang="ts">
	const sections = [
		{
			title: 'Getting Started',
			description: 'Learn how to set up and configure Dixie for your workflow.',
			steps: [
				'Install prerequisites (Node.js, Python 3)',
				'Clone the repository and install dependencies',
				'Configure your database connection',
				'Start the development server'
			]
		},
		{
			title: 'Dashboard',
			description: 'Understanding the analytics dashboard and its components.',
			steps: [
				'Overview of key metrics and KPIs',
				'Reading chart data and trends',
				'Customizing your dashboard layout',
				'Exporting reports'
			]
		},
		{
			title: 'Inventory Management',
			description: 'How to manage clients and inventory records.',
			steps: [
				'Adding and editing client records',
				'Searching and filtering inventory',
				'Bulk import/export operations',
				'Managing client categories'
			]
		},
		{
			title: 'Settings & Configuration',
			description: 'Configure application settings and user preferences.',
			steps: [
				'Account security and password management',
				'Notification preferences',
				'API key management',
				'Backup and restore'
			]
		},
		{
			title: 'API Reference',
			description: 'Technical documentation for the REST API.',
			steps: [
				'Authentication and authorization',
				'Available endpoints and methods',
				'Request/response formats',
				'Error handling and status codes'
			]
		},
		{
			title: 'Troubleshooting',
			description: 'Common issues and how to resolve them.',
			steps: [
				'Connection and network issues',
				'Database migration problems',
				'Performance optimization tips',
				'Contacting support'
			]
		}
	];
</script>

<div class="page">
	<div class="page-header">
		<h1>Documentation</h1>
		<p class="subtitle">Everything you need to know about Dixie</p>
	</div>

	<div class="intro-card card">
		<div class="intro-badge">v0.1.0</div>
		<h2>Welcome to Dixie</h2>
		<p>
			Dixie is a modern dashboard application for managing clients, tracking analytics,
			and streamlining your workflow. This documentation covers setup, usage, and
			configuration.
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
