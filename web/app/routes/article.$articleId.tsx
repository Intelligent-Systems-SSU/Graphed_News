import type { MetaFunction } from '@remix-run/cloudflare';
import { Await, useLoaderData } from '@remix-run/react';
import { Suspense } from 'react';
import createLoader from 'app/utils/createLoader';

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
    <div className="flex h-screen items-center justify-center p-20">
      <Suspense fallback={<div>Loading...</div>}>
        <Await resolve={data}>
          {(news) =>
            news ? (
              <div>
                <h1>{news.title}</h1>
                <p>{news.content}</p>
              </div>
            ) : (
              <div>Article not found</div>
            )
          }
        </Await>
      </Suspense>
    </div>
  );
}
