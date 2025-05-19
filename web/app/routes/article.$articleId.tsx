import type { MetaFunction } from '@remix-run/cloudflare';
import { Await, Link, useLoaderData } from '@remix-run/react';
import { Suspense } from 'react';
import createLoader from 'app/utils/createLoader';
import { News } from '@prisma/client';

export const meta: MetaFunction = () => {
  return [{ title: 'Article' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export const loader = createLoader(async ({ params, db }) => {
  if (!params.articleId) {
    throw new Error('Article ID is required');
  }

  const data = await db.news.findUnique({ where: { id: Number(params.articleId) } });

  return { data };
});

export default function Show() {
  const { data } = useLoaderData<typeof loader>();

  return (
    <div className="flex p-4 max-w-4xl mt-8 mx-auto">
      <Suspense fallback={<div>Loading...</div>}>
        <Await resolve={data}>{(news) => (news ? <NewsWrapper news={news} /> : <div>Article not found</div>)}</Await>
      </Suspense>
    </div>
  );
}

const NewsWrapper = ({ news }: { news: News }) => {
  return (
    <div>
      <Link to="/article" className="text-blue-500 hover:underline">
        {'⬅️ 리스트로'}
      </Link>
      <h1 className="text-3xl font-bold">{news.title}</h1>
      <div className="flex items-center gap-2 mt-1 md:mt-3">
        <p className="text-gray-500 text-sm">
          {news.createdAt.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })}
        </p>
        <a href={news.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 text-sm hover:underline">
          Read original
        </a>
      </div>
      <p className="mt-4">{news.content}</p>
    </div>
  );
};
