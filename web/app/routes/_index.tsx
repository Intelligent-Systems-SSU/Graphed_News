import type { MetaFunction } from '@remix-run/cloudflare';
import { Link } from '@remix-run/react';

export const meta: MetaFunction = () => {
  return [{ title: 'New Remix App' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export default function Index() {
  return (
    <div className="flex h-screen items-center justify-center">
      <Link to="/article" className="text-blue-500 hover:underline">
        기사 리스트
      </Link>
    </div>
  );
}
