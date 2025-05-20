import type { MetaFunction } from '@remix-run/cloudflare';
import { Suspense } from 'react';
import { Link, Await, useLoaderData } from '@remix-run/react';
import createLoader from 'app/utils/createLoader';
import { News, NewsSummary } from '@prisma/client';
import { getPrismaClient } from 'app/utils/prisma';

export const meta: MetaFunction = () => {
  return [{ title: 'Article' }, { name: 'description', content: 'Welcome to Remix!' }];
};

const loadSummary = async (db: ReturnType<typeof getPrismaClient>, articleId: string) => {
  return await db.newsSummary.findUnique({ where: { newsId: Number(articleId) } });
};

export const loader = createLoader(async ({ params, db }) => {
  if (!params.articleId) {
    throw new Error('Article ID is required');
  }

  const news = await db.news.findUnique({ where: { id: Number(params.articleId) } });
  const summary = loadSummary(db, params.articleId);

  return { news, summary };
});

export default function Show() {
  const data = useLoaderData<typeof loader>();
  const { news, summary } = data;

  return (
    <div className="flex p-4 max-w-4xl mt-8 mx-auto">
      {news ? <NewsWrapper news={news} summary={summary} /> : <div>Article not found</div>}
    </div>
  );
}

const NewsWrapper = ({ news, summary }: { news: News; summary: Promise<NewsSummary | null> }) => {
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
          <Suspense fallback={<p>불러오는 중...</p>}>
            <Await resolve={summary}>
              {(summary) => (
                <p className="text-sm text-gray-700 break-words">{summary?.summary ?? '요약이 없습니다.'}</p>
              )}
            </Await>
          </Suspense>
        </div>
      </div>
    </div>
  );
};
