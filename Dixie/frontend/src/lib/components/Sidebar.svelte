<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { theme } from '$lib/stores/theme.svelte';

	async function handleLogout() {
		await fetch('/api/logout', { method: 'POST' });
		goto('/login');
	}

	const navItems = [
		{
			label: 'Dashboard',
			href: '/dashboard',
			icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-4 0a1 1 0 01-1-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 01-1 1'
		},
		{
			label: 'Management',
			href: '/management',
			icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
		},
		{
			label: 'Documentation',
			href: '/documentation',
			icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
		},
		{
			label: 'Settings',
			href: '/settings',
			icon: 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z'
		}
	];

	function isActive(href: string): boolean {
		return page.url.pathname === href || page.url.pathname.startsWith(href + '/');
	}
</script>

<aside class="sidebar">
	<div class="logo">
		<div class="logo-icon">D</div>
		<span class="logo-text">Dixie</span>
	</div>

	<nav class="nav">
		{#each navItems as item}
			<a href={item.href} class="nav-item" class:active={isActive(item.href)}>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
					stroke-linecap="round"
					stroke-linejoin="round"
				>
					<path d={item.icon} />
				</svg>
				<span>{item.label}</span>
			</a>
		{/each}
	</nav>

	<div class="sidebar-footer">
		<button class="theme-toggle" onclick={() => theme.toggle()}>
			{#if theme.dark}
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
					<circle cx="12" cy="12" r="5" />
					<line x1="12" y1="1" x2="12" y2="3" />
					<line x1="12" y1="21" x2="12" y2="23" />
					<line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
					<line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
					<line x1="1" y1="12" x2="3" y2="12" />
					<line x1="21" y1="12" x2="23" y2="12" />
					<line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
					<line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
				</svg>
				<span>Light Mode</span>
			{:else}
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
				</svg>
				<span>Dark Mode</span>
			{/if}
		</button>

		<button class="theme-toggle" onclick={handleLogout}>
			<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
				<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
				<polyline points="16 17 21 12 16 7" />
				<line x1="21" y1="12" x2="9" y2="12" />
			</svg>
			<span>Log Out</span>
		</button>
	</div>
</aside>

<style>
	.sidebar {
		position: fixed;
		top: 0;
		left: 0;
		width: 240px;
		height: 100vh;
		background-color: var(--color-sidebar-bg);
		display: flex;
		flex-direction: column;
		padding: 1.5rem 0;
		z-index: 50;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0 1.5rem;
		margin-bottom: 2rem;
	}

	.logo-icon {
		width: 36px;
		height: 36px;
		background: linear-gradient(135deg, #a855f7, #7e22ce);
		border-radius: 10px;
		display: flex;
		align-items: center;
		justify-content: center;
		color: white;
		font-weight: 700;
		font-size: 1.1rem;
	}

	.logo-text {
		color: #ffffff;
		font-size: 1.25rem;
		font-weight: 600;
		letter-spacing: -0.02em;
	}

	.nav {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
		padding: 0 0.75rem;
		flex: 1;
	}

	.nav-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.625rem 0.75rem;
		border-radius: 8px;
		color: #a1a1b5;
		text-decoration: none;
		font-size: 0.875rem;
		font-weight: 500;
		transition: all 0.15s ease;
	}

	.nav-item:hover {
		background-color: var(--color-sidebar-hover);
		color: #ffffff;
	}

	.nav-item.active {
		background-color: var(--color-sidebar-active);
		color: #ffffff;
	}

	.sidebar-footer {
		padding: 0 0.75rem;
		border-top: 1px solid rgba(255, 255, 255, 0.08);
		padding-top: 1rem;
	}

	.theme-toggle {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 0.625rem 0.75rem;
		border-radius: 8px;
		color: #a1a1b5;
		background: none;
		border: none;
		cursor: pointer;
		font-size: 0.875rem;
		font-weight: 500;
		width: 100%;
		transition: all 0.15s ease;
	}

	.theme-toggle:hover {
		background-color: var(--color-sidebar-hover);
		color: #ffffff;
	}
</style>
