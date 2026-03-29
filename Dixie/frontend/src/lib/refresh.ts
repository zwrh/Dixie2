import { browser } from '$app/environment';

const REFRESH_INTERVAL = 15_000; // 15 seconds
let interval: ReturnType<typeof setInterval> | null = null;
let listeners = new Set<() => void>();

function tick() {
	for (const fn of listeners) {
		fn();
	}
}

export function onRefresh(fn: () => void): () => void {
	listeners.add(fn);

	if (browser && listeners.size === 1 && !interval) {
		interval = setInterval(tick, REFRESH_INTERVAL);
	}

	return () => {
		listeners.delete(fn);
		if (listeners.size === 0 && interval) {
			clearInterval(interval);
			interval = null;
		}
	};
}
