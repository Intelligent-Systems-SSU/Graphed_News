import type { MetaFunction } from '@remix-run/cloudflare';
import { Link } from '@remix-run/react';

export const meta: MetaFunction = () => {
  return [{ title: '기사 리스트' }, { name: 'description', content: 'AI로 요약된 기사를 확인해 보세요.' }];
};

export default function Index() {
  return (
    <div className="flex max-w-4xl mx-auto px-4 pt-5">
      <Link to="/article" className="text-blue-500 hover:underline">
        기사 리스트
      </Link>
    </div>
  );
}
