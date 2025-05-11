import type { MetaFunction } from '@remix-run/cloudflare';
import { Link, useLoaderData } from '@remix-run/react';
import { getSummary } from 'app/API/AI/AI';

export const meta: MetaFunction = () => {
  return [{ title: 'New Remix App' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export const loader = async () => {
  const summary = await getSummary().catch((error) => {
    console.error('Error while fetching summary:', error);
    return 'Error while fetching summary';
  });

  return {
    summary,
  };
};

export default function Index() {
  const { summary } = useLoaderData<typeof loader>();

  return (
    <div className="flex h-screen items-center justify-center">
      <Link to="/article" className="text-blue-500 hover:underline">
        기사 리스트
      </Link>
      <div>{summary}</div>
    </div>
  );
}
