import { redirect } from '@sveltejs/kit';
import { authFetch } from '$lib/auth';
import type { LayoutLoad } from './$types';

export const ssr = false;

export const load: LayoutLoad = async () => {
	try {
		const res = await authFetch('/api/me');
		if (!res.ok) {
			throw redirect(302, '/login');
		}
		return { user: await res.json() };
	} catch (e) {
		if (e && typeof e === 'object' && 'status' in e) throw e;
		throw redirect(302, '/login');
	}
};
