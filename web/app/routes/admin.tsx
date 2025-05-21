import type { MetaFunction } from '@remix-run/cloudflare';
import { useActionData } from '@remix-run/react';
import { getSummary } from 'app/API/AI/AI';
import createAction from 'app/utils/createAction';

export const meta: MetaFunction = () => {
  return [{ title: 'New Remix App' }, { name: 'description', content: 'Welcome to Remix!' }];
};

export const action = createAction(async ({ request }) => {
  const url = (await request.formData()).get('url') as string;
  const success = await getSummary(url)
    .then(() => true)
    .catch(() => false);
  return { success };
});

export default function Index() {
  const actionData = useActionData<typeof action>();

  return (
    <div className="flex flex-col max-w-4xl mx-auto px-4 pt-5">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">테스트 페이지</h1>
      <form method="post" className="flex gap-2">
        <input type="text" name="url" className="border border-gray-300 rounded px-2 py-1" />
        <button className="bg-blue-500 text-white px-4 py-2 rounded" type="submit">
          테스트
        </button>
      </form>
      {actionData && <p>{actionData.success ? '성공' : '실패'}</p>}
    </div>
  );
}
