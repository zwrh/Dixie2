<script lang="ts">
	import { page } from '$app/state';
	import { onMount, onDestroy } from 'svelte';
	import { getToken, authFetch } from '$lib/auth';
	import { io, type Socket } from 'socket.io-client';
	import { Terminal } from '@xterm/xterm';
	import { FitAddon } from '@xterm/addon-fit';
	import '@xterm/xterm/css/xterm.css';

	const clientId = parseInt(page.params.clientId);

	let terminalEl: HTMLDivElement;
	let term: Terminal;
	let fitAddon: FitAddon;
	let sock: Socket;
	let resizeObs: ResizeObserver;

	let status = $state<'loading' | 'waiting' | 'connected' | 'error' | 'closed'>('loading');
	let errorMessage = $state('');
	let clientInfo = $state<{ identifier: string; ip_address: string } | null>(null);

	const statusLabel: Record<string, string> = {
		loading: 'Loading',
		waiting: 'Waiting for shell',
		connected: 'Connected',
		error: 'Error',
		closed: 'Disconnected'
	};

	onMount(async () => {
		const res = await authFetch(`/api/clients/${clientId}`);
		if (!res.ok) {
			status = 'error';
			errorMessage = 'Client not found';
			return;
		}
		clientInfo = await res.json();

		term = new Terminal({
			cursorBlink: true,
			theme: {
				background: '#0d1117',
				foreground: '#c9d1d9',
				cursor: '#1aaf92'
			},
			fontFamily: "'SF Mono', 'Fira Code', monospace",
			fontSize: 14
		});
		fitAddon = new FitAddon();
		term.loadAddon(fitAddon);
		term.open(terminalEl);
		fitAddon.fit();

		resizeObs = new ResizeObserver(() => fitAddon.fit());
		resizeObs.observe(terminalEl);

		sock = io('/', {
			auth: { token: getToken() },
			transports: ['websocket']
		});

		sock.on('connect', () => {
			sock.emit('start_terminal', { client_id: clientId });
			status = 'waiting';
			term.writeln('Triggering reverse shell...');
		});

		sock.on('terminal_waiting', () => {
			status = 'waiting';
		});

		sock.on('terminal_ready', () => {
			status = 'connected';
			term.writeln('\r\nSession established.\r\n');
			term.focus();
		});

		sock.on('terminal_output', (msg: { data: string }) => {
			term.write(msg.data);
		});

		sock.on('terminal_error', (msg: { message: string }) => {
			status = 'error';
			errorMessage = msg.message;
			term.writeln(`\r\n[ERROR] ${msg.message}`);
		});

		sock.on('terminal_closed', () => {
			status = 'closed';
			term.writeln('\r\n[Session closed]');
		});

		sock.on('connect_error', (err: Error) => {
			status = 'error';
			errorMessage = 'WebSocket connection failed: ' + err.message;
		});

		term.onData((data: string) => {
			if (status === 'connected') {
				sock.emit('terminal_input', { data });
			}
		});
	});

	onDestroy(() => {
		if (sock) sock.disconnect();
		if (term) term.dispose();
		if (resizeObs) resizeObs.disconnect();
	});
</script>

<div class="page">
	<div class="page-header">
		<div class="header-top">
			<a href="/terminal" class="back-link">&larr; Back</a>
		</div>
		<h1>Terminal</h1>
		<p class="subtitle">
			{#if clientInfo}
				{clientInfo.identifier} &mdash; {clientInfo.ip_address}
			{:else}
				Connecting...
			{/if}
		</p>
	</div>

	<div class="card terminal-card">
		<div class="terminal-status-bar">
			<span
				class="status-dot"
				class:connected={status === 'connected'}
				class:waiting={status === 'waiting'}
				class:error={status === 'error'}
			></span>
			<span class="status-text">{statusLabel[status] ?? status}</span>
			{#if errorMessage && status === 'error'}
				<span class="error-msg">{errorMessage}</span>
			{/if}
		</div>
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<!-- svelte-ignore a11y_no_static_element_interactions -->
		<div class="terminal-container" bind:this={terminalEl} onclick={() => term?.focus()}></div>
	</div>
</div>

<style>
	.page {
		max-width: 1100px;
		margin: 0 auto;
	}

	.page-header {
		margin-bottom: 1.25rem;
	}

	.header-top {
		margin-bottom: 0.5rem;
	}

	.back-link {
		font-size: 0.8rem;
		color: #1aaf92;
		text-decoration: none;
		font-weight: 500;
	}

	.back-link:hover {
		text-decoration: underline;
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
		font-family: 'SF Mono', 'Fira Code', monospace;
	}

	.card {
		background-color: var(--color-card-bg);
		border: 1px solid var(--color-border);
		border-radius: 12px;
		overflow: hidden;
	}

	.terminal-card {
		padding: 0;
	}

	.terminal-status-bar {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 1rem;
		border-bottom: 1px solid var(--color-border);
		font-size: 0.75rem;
		color: var(--color-text-muted);
	}

	.status-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: #6b7280;
		flex-shrink: 0;
	}

	.status-dot.connected {
		background: #22c55e;
	}

	.status-dot.waiting {
		background: #f59e0b;
		animation: pulse 2s infinite;
	}

	.status-dot.error {
		background: #ef4444;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.4;
		}
	}

	.status-text {
		font-weight: 500;
	}

	.error-msg {
		color: #ef4444;
		font-size: 0.7rem;
		margin-left: auto;
	}

	.terminal-container {
		height: 520px;
		background: #0d1117;
		padding: 0.5rem;
	}

	.terminal-container :global(.xterm) {
		height: 100%;
	}
</style>
