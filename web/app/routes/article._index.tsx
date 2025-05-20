import type { MetaFunction } from '@remix-run/cloudflare';
import { Await, Link, useLoaderData } from '@remix-run/react';
import { Suspense } from 'react';
import createLoader from 'app/utils/createLoader';
import ExternalLinkIcon from 'app/components/ExternalLinkIcon';

export const meta: MetaFunction = () => {
  return [{ title: '기사 리스트' }, { name: 'description', content: 'AI로 요약된 기사를 확인해보세요.' }];
};

export const loader = createLoader(async ({ db }) => {
  const data = await db.news.findMany({ take: 10 });
  return { data };
});

export default function Index() {
  const { data } = useLoaderData<typeof loader>();

  return (
    <div className="max-w-4xl mx-auto px-4 pt-5 pb-8 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">기사 목록</h1>
      <Suspense
        fallback={
          <div className="space-y-8">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse space-y-4">
                <div className="h-6 bg-gray-200 rounded w-3/4"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
              </div>
            ))}
          </div>
        }
      >
        <Await resolve={data}>
          {(resolvedData) => (
            <div className="space-y-6">
              {resolvedData.map((item) => (
                <article
                  key={item.id}
                  className="bg-white overflow-hidden rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 border border-gray-100"
                >
                  <Link
                    to={`/article/${item.id}`}
                    className="block p-6 hover:bg-gray-50 transition-colors duration-150"
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h2 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">{item.title}</h2>
                        <p className="text-gray-600 text-sm mb-3 line-clamp-3">
                          {item.content.replace(/<[^>]*>?/gm, '').slice(0, 200)}
                          {item.content.length > 200 && '...'}
                        </p>
                      </div>
                      {item.url && (
                        <a
                          href={item.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 font-medium text-sm inline-flex items-center"
                        >
                          원문 보기
                          <ExternalLinkIcon />
                        </a>
                      )}
                    </div>
                    <div className="mt-3 flex items-center text-sm text-gray-500">
                      <span>{new Date(item.createdAt).toLocaleDateString('ko-KR')}</span>
                    </div>
                  </Link>
                </article>
              ))}
            </div>
          )}
        </Await>
      </Suspense>
    </div>
  );
}
