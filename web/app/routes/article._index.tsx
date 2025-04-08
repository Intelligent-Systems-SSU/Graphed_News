import type { MetaFunction } from '@remix-run/node';
import { Await, Link, useLoaderData } from '@remix-run/react';
import { Suspense } from 'react';
import { newsApi } from 'app/API/NewsApi/newsApi';

export const meta: MetaFunction = () => {
  return [{ title: 'New Remix App' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export default function Index() {
  const { data } = useLoaderData<typeof loader>();

  return (
    <div className="flex flex-col h-screen items-center justify-center p-20">
      <Suspense fallback={<div>Loading...</div>}>
        <Await resolve={data}>
          {(resolvedData) =>
            resolvedData.map((item) => (
              <div key={item.id} className="p-4 border w-full">
                <Link to={`/article/${item.id}`} className="text-blue-500 hover:underline">
                  <h2 className="text-xl font-bold">{item.title}</h2>
                </Link>
                <p>{item.content}</p>
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  Read more
                </a>
              </div>
            ))
          }
        </Await>
      </Suspense>
    </div>
  );
}

export const loader = async () => {
  const data = newsApi.getNewsList();
  return { data };
};
