import type { MetaFunction } from '@remix-run/cloudflare';
import { Await, Link, useLoaderData } from '@remix-run/react';
import { Suspense } from 'react';
import createLoader from 'app/utils/createLoader';
import { News, NewsSummary } from '@prisma/client';

export const meta: MetaFunction = () => {
  return [{ title: 'Article' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export const loader = createLoader(async ({ params, db }) => {
  if (!params.articleId) {
    throw new Error('Article ID is required');
  }

  const news = await db.news.findUnique({ where: { id: Number(params.articleId) } });
  const summary = await db.newsSummary.findUnique({ where: { newsId: Number(params.articleId) } });

  return { news, summary };
});

export default function Show() {
  const { news, summary } = useLoaderData<typeof loader>();

  return (
    <div className="flex p-4 max-w-4xl mt-8 mx-auto">
      <Suspense fallback={<div>Loading...</div>}>
        <Await resolve={news}>
          {(news) => (news ? <NewsWrapper news={news} summary={summary} /> : <div>Article not found</div>)}
        </Await>
      </Suspense>
    </div>
  );
}

const NewsWrapper = ({ news, summary }: { news: News; summary: NewsSummary | null }) => {
  return (
    <div className="w-full">
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
      <div className="mt-4 flex flex-col md:flex-row w-full gap-4">
        <p className="w-full md:w-2/3">{news.content}</p>
        <div className="w-full md:w-1/3 bg-gray-50 p-4 rounded-lg">
          <h3 className="font-bold mb-2">요약</h3>
          <p className="text-sm text-gray-700 break-words">{summary?.summary || '요약이 없습니다.'}</p>
        </div>
      </div>
    </div>
  );
};
