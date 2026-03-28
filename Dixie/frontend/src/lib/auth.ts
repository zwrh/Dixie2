import { browser } from '$app/environment';

const TOKEN_KEY = 'dixie_token';

export function getToken(): string | null {
	if (!browser) return null;
	return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
	if (browser) localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
	if (browser) localStorage.removeItem(TOKEN_KEY);
}

export function authFetch(url: string, opts: RequestInit = {}): Promise<Response> {
	const token = getToken();
	const headers = new Headers(opts.headers);
	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}
	return fetch(url, { ...opts, headers });
}
