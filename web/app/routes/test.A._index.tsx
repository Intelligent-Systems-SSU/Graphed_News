import { Form } from '@remix-run/react';
import { redirect } from '@remix-run/cloudflare';
import createAction from 'app/utils/createAction';

export const action = createAction(async ({ db, request }) => {
  const form = await request.formData();
  const testId = 1;
  const name = form.get('name') as string | null;
  const time = null; // float 초 단위 시간

  const testSolve = await db.testSolve.create({
    data: {
      testType: 'A',
      testId,
      name: name ?? '익명',
      time,
    },
  });

  return redirect(`/test/${testId}/solve/${testSolve.id}`);
});

export default function ATestPage() {
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">뉴스 기사 테스트 페이지 (A 테스터)</h1>

      <section className="mb-10">
        <p className="text-lg leading-relaxed">
          A 테스터는 <strong>SSU KA NEWS에서 AI가 요약·정리해준 기사</strong>를 읽고 퀴즈에 응시하게 됩니다.
        </p>
        <p className="text-lg leading-relaxed mt-4">
          준비가 되셨다면 아래 기사 링크를 클릭하여 요약 기사를 읽은 후, 퀴즈에 응시해 주세요.
        </p>
      </section>

      <section className="mb-16 space-y-8">
        <div>
          <h2 className="text-xl font-semibold mb-2">📄 기사 링크</h2>
          <a
            href="http://localhost:5173/article/1" // 실제 요약 기사 링크로 변경 필요
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline text-lg"
          >
            요약 기사 바로가기
          </a>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-2">📝 퀴즈 응시하기</h2>
          <Form method="post" className="space-y-4">
            {/* 이름 입력 필드 */}
            <input
              type="text"
              name="name"
              placeholder="이름을 입력해주세요"
              className="w-full border border-gray-300 rounded-md px-4 py-2 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-400"
              required
            />
            <button type="submit" className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-md text-lg">
              퀴즈 시작
            </button>
          </Form>
        </div>
      </section>

      <div className="text-sm text-gray-500 mt-10">
        <a href="/" className="underline hover:text-blue-500">
          ← 홈으로 돌아가기
        </a>
      </div>
    </div>
  );
}
