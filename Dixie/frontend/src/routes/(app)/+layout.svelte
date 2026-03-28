<script lang="ts">
	import Sidebar from '$lib/components/Sidebar.svelte';

	let { children } = $props();
</script>

<div class="app-layout">
	<Sidebar />
	<main class="main-content">
		{@render children()}
	</main>
</div>

<style>
	.app-layout {
		display: flex;
		min-height: 100vh;
	}

	.main-content {
		margin-left: 240px;
		flex: 1;
		padding: 2rem;
		background-color: var(--color-surface-alt);
		min-height: 100vh;
	}
</style>
