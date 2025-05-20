import type { MetaFunction } from '@remix-run/cloudflare';
import { Suspense } from 'react';
import { Link, Await, useLoaderData } from '@remix-run/react';
import createLoader from 'app/utils/createLoader';
import { News, NewsSummary } from '@prisma/client';
import { getPrismaClient } from 'app/utils/prisma';
import ExternalLinkIcon from 'app/components/ExternalLinkIcon';

type NewsWithStringDate = Omit<News, 'createdAt'> & {
  createdAt: string;
};

export const meta: MetaFunction<typeof loader> = ({ data }) => {
  return [
    { title: data?.news?.title || 'Article' },
    {
      name: 'description',
      content: data?.news?.content.replace(/<\/?[^>]+(>|$)/g, '').slice(0, 70) || '기사 요약을 확인해보세요.',
    },
  ];
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
    <div className="flex max-w-4xl mx-auto">
      {news ? (
        <NewsWrapper news={news as unknown as NewsWithStringDate} summary={summary} />
      ) : (
        <div>Article not found</div>
      )}
    </div>
  );
}

const NewsWrapper = ({ news, summary }: { news: NewsWithStringDate; summary: Promise<NewsSummary | null> }) => {
  return (
    <div className="max-w-4xl mx-auto px-4 pt-2 pb-8 sm:px-6 lg:px-8">
      <BackToListLink />

      <article className="bg-white rounded-lg">
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4 leading-tight">{news.title}</h1>
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 border-b pb-6">
            <time dateTime={new Date(news.createdAt).toISOString()}>
              {new Date(news.createdAt).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </time>
            {news.url && (
              <a
                href={news.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center"
              >
                원문 보기
                <ExternalLinkIcon />
              </a>
            )}
          </div>
        </header>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="lg:w-2/3">
            <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: news.content }} />
          </div>

          <aside className="lg:w-1/3">
            <div className="bg-gray-50 rounded-lg p-5 lg:p-5 sm:p-3 sticky top-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 pb-2 border-b border-gray-200">기사 요약</h2>
              <Suspense
                fallback={
                  <div className="animate-pulse space-y-3">
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                    <div className="h-4 bg-gray-200 rounded w-4/6"></div>
                  </div>
                }
              >
                <Await resolve={summary}>
                  {(summary) => (
                    <div
                      className="prose-sm text-gray-700"
                      dangerouslySetInnerHTML={{
                        __html:
                          summary?.summary?.replace(/\n/g, '<br>') || '<p class="text-gray-500">요약이 없습니다.</p>',
                      }}
                    />
                  )}
                </Await>
              </Suspense>
            </div>
          </aside>
        </div>
      </article>
    </div>
  );
};

const BackToListLink = () => (
  <div className="mb-4">
    <Link
      to="/article"
      className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium transition-colors duration-150"
    >
      <svg
        className="w-4 h-4 mr-1"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      목록으로 돌아가기
    </Link>
  </div>
);
