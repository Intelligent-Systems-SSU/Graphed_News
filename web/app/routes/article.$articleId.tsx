import type { LoaderFunctionArgs, MetaFunction } from '@remix-run/cloudflare';
import { Suspense } from 'react';
import { Link, Await, useLoaderData } from '@remix-run/react';
import { Tooltip } from 'react-tooltip';
import 'react-tooltip/dist/react-tooltip.css';

import { News, NewsSummary } from '@prisma/client';
import createLoader from 'app/utils/createLoader';
import { getPrismaClient } from 'app/utils/prisma';
import { annotateContent, RefItem } from 'app/utils/annotate';
import ExternalLinkIcon from 'app/components/ExternalLinkIcon';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import remarkGfm from 'remark-gfm';

/* ---------- 타입 ---------- */
type NewsWithStringDate = Omit<News, 'createdAt'> & { createdAt: string };
type KeywordRow = { keyword: string; description: string };

/* ---------- <head> ---------- */
export const meta: MetaFunction<typeof loader> = ({ data }) => [
  { title: data?.news?.title ?? 'Article' },
  {
    name: 'description',
    content: data?.news?.content.replace(/<\/?[^>]+(>|$)/g, '').slice(0, 70) ?? '기사 요약을 확인해보세요.',
  },
];

const loadSummary = async (db: ReturnType<typeof getPrismaClient>, articleId: string) => {
  return await db.newsSummary.findUnique({ where: { newsId: Number(articleId) } });
};

/* ---------- 로더 ---------- */
export const loader = createLoader(
  async ({ params, db }: LoaderFunctionArgs & { db: ReturnType<typeof getPrismaClient> }) => {
    if (!params.articleId) throw new Error('Article ID is required');
    const id = Number(params.articleId);

    const news = await db.news.findUnique({
      where: { id },
      include: { newsKeyword: { select: { keyword: true, description: true } } },
    });
    if (!news) throw new Response('Not Found', { status: 404 });
    const summary = loadSummary(db, params.articleId);

    const { annotated, refs } = annotateContent(news.content, news.newsKeyword as KeywordRow[]);

    return {
      news: { ...news, content: annotated, createdAt: news.createdAt.toISOString() },
      refs,
      summary,
    };
  }
);

/* ---------- 페이지 ---------- */
export default function ArticleRoute() {
  const { news, refs, summary } = useLoaderData<typeof loader>();
  if (!news) return <div>Article not found</div>;

  return (
    <div className="flex max-w-4xl mx-auto">
      <NewsBody news={news as NewsWithStringDate} refs={refs} summary={summary} />

      {/* 🟦 전역 툴팁: .kw-ref 요소 대상으로 활성화 */}
      <Tooltip
        id="kwTip"
        anchorSelect=".kw-ref"
        place="bottom"
        className="!z-50 max-w-xs rounded-xl border bg-white px-3 py-2 text-sm shadow"
      />
    </div>
  );
}

/* ---------- 본문 + 각주 + 요약 ---------- */
function NewsBody({
  news,
  refs,
  summary,
}: {
  news: NewsWithStringDate;
  refs: RefItem[];
  summary: Promise<NewsSummary | null>;
}) {
  return (
    <div className="max-w-4xl mx-auto px-4 pt-6 pb-8 sm:px-6 lg:px-8">
      <BackToListLink />

      <article className="bg-white rounded-lg">
        {/* 헤더 */}
        <header className="mb-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">{news.title}</h1>
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 border-b pb-6">
            <time dateTime={news.createdAt}>
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

        {/* 본문 & 요약 */}
        <div className="flex flex-col lg:flex-col gap-8">
          <aside>
            <div className="bg-gray-50 rounded-lg p-5 sticky top-6">
              <h2 className="text-lg font-semibold mb-4 pb-2 border-b"> 🔍 기사 심층 요약 </h2>
              <Suspense
                fallback={
                  <div className="animate-pulse space-y-3">
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                    <div className="h-4 bg-gray-200 rounded w-4/6"></div>
                  </div>
                }
              >
                <article className="prose">
                  <Await resolve={summary}>
                    {(summary) =>
                      summary?.summary ? (
                        <ReactMarkdown
                          children={summary.summary}
                          remarkPlugins={[remarkGfm]} // GFM (테이블, 취소선 등) 활성화
                          rehypePlugins={[rehypeRaw]} // HTML 렌더링 허용 (주의해서 사용)
                          // rehypePlugins={[rehypeRaw, rehypeSanitize]} // HTML을 렌더링하되, 보안을 위해 sanitize 처리
                        />
                      ) : (
                        <p className="text-gray-500">요약이 없습니다.</p>
                      )
                    }
                  </Await>
                </article>
              </Suspense>
            </div>
          </aside>
          {/* 본문 */}
          <div>
            <div
              className="prose max-w-none"
              // eslint-disable-next-line react/no-danger
              dangerouslySetInnerHTML={{ __html: news.content }}
            />

            {/* ---------- 각주 목록 ---------- */}
            {refs.length > 0 && (
              <section id="references" className="mt-10">
                <hr className="my-6" />
                <h2 className="text-lg font-semibold mb-4">주석</h2>
                <ol className="list-decimal pl-6 space-y-2">
                  {refs.map(({ order, description }) => (
                    <li key={order} id={`note-${order}`}>
                      <p className="inline">
                        {description}{' '}
                        <a href={`#cite-${order}`} className="text-blue-600 ml-1">
                          ↩︎
                        </a>
                      </p>
                    </li>
                  ))}
                </ol>
              </section>
            )}
          </div>
        </div>
      </article>
    </div>
  );
}

/* ---------- 목록 링크 ---------- */
const BackToListLink = () => (
  <div className="mb-4">
    <Link to="/article" className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium">
      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
      </svg>
      목록으로 돌아가기
    </Link>
  </div>
);
