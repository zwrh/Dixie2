import { browser } from '$app/environment';

function getInitialTheme(): boolean {
	if (browser) {
		const saved = localStorage.getItem('theme');
		if (saved) return saved === 'dark';
		return window.matchMedia('(prefers-color-scheme: dark)').matches;
	}
	return false;
}

function applyTheme(isDark: boolean) {
	if (browser) {
		document.documentElement.classList.toggle('dark', isDark);
		localStorage.setItem('theme', isDark ? 'dark' : 'light');
	}
}

let dark = $state(getInitialTheme());

// Apply on initial load
if (browser) {
	applyTheme(dark);
}

export const theme = {
	get dark() {
		return dark;
	},
	toggle() {
		dark = !dark;
		applyTheme(dark);
	}
};
