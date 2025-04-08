import type { LoaderFunctionArgs, MetaFunction } from '@remix-run/cloudflare';
import { Await, useLoaderData } from '@remix-run/react';
import { Suspense } from 'react';
import { newsApi } from 'app/API/NewsApi/newsApi';

export const meta: MetaFunction = () => {
  return [{ title: 'Article' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export default function Show() {
  const { promiseNews, promiseBackground } = useLoaderData<typeof loader>();

  return (
    <div className="flex h-screen items-center justify-center p-20">
      <Suspense fallback={<div>Loading...</div>}>
        <Await resolve={promiseNews}>
          {(news) => (
            <div>
              <h1>{news.title}</h1>
              <p>{news.content}</p>
            </div>
          )}
        </Await>
      </Suspense>
      <Suspense fallback={<div>Loading...</div>}>
        <Await resolve={promiseBackground}>
          {(background) => (
            <div>
              <h2>Background</h2>
              {background.map((bg) => (
                <div key={bg.id}>
                  <p>{bg.content}</p>
                </div>
              ))}
            </div>
          )}
        </Await>
      </Suspense>
    </div>
  );
}

export const loader = async ({ params }: LoaderFunctionArgs) => {
  if (!params.articleId) {
    throw new Error('Article ID is required');
  }
  const promiseNews = newsApi.getNewsById(params.articleId);
  const promiseBackground = newsApi.getNewsBackground(params.articleId);
  return { promiseNews, promiseBackground };
};
