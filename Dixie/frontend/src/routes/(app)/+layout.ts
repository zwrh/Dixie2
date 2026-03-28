import { redirect } from '@sveltejs/kit';
import type { LayoutLoad } from './$types';

export const ssr = false;

export const load: LayoutLoad = async ({ fetch }) => {
	const res = await fetch('/api/me');
	if (!res.ok) {
		throw redirect(302, '/login');
	}
	return { user: await res.json() };
};
