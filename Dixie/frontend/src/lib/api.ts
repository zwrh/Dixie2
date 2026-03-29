let token: string | null = localStorage.getItem('token');

export function setToken(t: string) {
	token = t;
	localStorage.setItem('token', t);
}

export function clearToken() {
	token = null;
	localStorage.removeItem('token');
}

export async function api(path: string, options: RequestInit = {}): Promise<Response> {
	const headers = new Headers(options.headers);
	if (token) {
		headers.set('Authorization', `Bearer ${token}`);
	}
	return fetch(path, { ...options, headers });
}
