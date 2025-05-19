import type { MetaFunction } from '@remix-run/cloudflare';
import { Await, useLoaderData } from '@remix-run/react';
import { getSummary } from 'app/API/AI/AI';
import createAction from 'app/utils/createAction';
import createLoader from 'app/utils/createLoader';
import { Suspense } from 'react';

export const meta: MetaFunction = () => {
  return [{ title: 'New Remix App' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export const loader = createLoader(async ({ db }) => {
  const summary = getSummary().catch((error) => {
    return 'Error while fetching summary';
  });

  const test = await db.test.findFirst();

  return {
    summary,
    test,
  };
});

export const action = createAction(async ({ db }) => {
  console.log('test');
  return null;
});

export default function Index() {
  const { summary, test } = useLoaderData<typeof loader>();

  return (
    <div className="flex h-screen items-center justify-center flex-col">
      <h1>테스트 페이지</h1>
      <Suspense fallback={<div>Loading...</div>}>
        <Await resolve={summary}>{(summary) => <p>{summary}</p>}</Await>
      </Suspense>
      <p>{test?.name}</p>
      <form method="post">
        <button type="submit">테스트</button>
      </form>
    </div>
  );
}
