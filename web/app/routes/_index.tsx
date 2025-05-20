import type { MetaFunction } from '@remix-run/cloudflare';
import { Link } from '@remix-run/react';

export const meta: MetaFunction = () => {
  return [{ title: '기사 리스트' }, { name: 'description', content: 'AI로 요약된 기사를 확인해 보세요.' }];
};

export default function Index() {
  return (
    <div className="flex p-4 max-w-4xl mt-8 mx-auto">
      <Link to="/article" className="text-blue-500 hover:underline">
        기사 리스트
      </Link>
    </div>
  );
}
