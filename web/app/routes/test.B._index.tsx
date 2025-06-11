import { Form } from '@remix-run/react';
import { redirect } from '@remix-run/cloudflare';
import createAction from 'app/utils/createAction';

export const action = createAction(async ({ db, request }) => {
  const form = await request.formData();
  const testType = 'B';
  const name = form.get('name') as string | null;
  const time = null;

  const testSolve = await db.testSolve.create({
    data: {
      testType,
      name: name ?? '익명',
      time,
    },
  });

  return redirect(`/test/solve/${testSolve.id}`);
});

export default function BTestPage() {
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">뉴스 기사 테스트 페이지 (B 테스터)</h1>

      <section className="mb-10">
        <p className="text-lg leading-relaxed">
          저희는 대학 수업 프로젝트의 일환으로, 기사를 보다 깊이 있게 이해할 수 있도록 돕는 ‘심층 요약 AI 기반 뉴스
          서비스’를 개발하고 있습니다.
          <br /> 이 서비스는 단순히 기사를 요약하는 것이 아니라, 전후 맥락과 배경지식까지 반영해 기사 내용을 풍부하게
          전달하는 AI 요약 기술을 바탕으로, 독자에게 더 깊은 이해를 제공하는 뉴스 읽기 경험을 목표로 합니다. <br />
          해당 서비스의 정확성과 학습 효과를 검증하기 위해, 현재 간단한 AB 테스트를 진행 중입니다.
          <br />
          <br /> <strong>B 테스터</strong>는 <strong>기사 원문</strong>을 읽고 간단한 퀴즈를 응시하여{' '}
          <strong>얼마나 시간이 걸렸는지</strong>를 확인할 것입니다.
        </p>
        <p className="text-m mt-4">
          ⏰ 소요 시간: 약 5분
          <br />
          🎯 사용 목적: 수업 프로젝트의 통계 분석 <br /> 🥸 익명 보장: 이름·이메일 등 개인 정보는 수집하지 않으며,
          이름은 임의로 자유롭게 입력하셔도 됩니다. <br />
          🗑️ 데이터 처리: 학기 종료 후 모든 응답은 영구적으로 폐기됩니다.
        </p>
      </section>

      <section className="mb-16 space-y-8">
        <div>
          <h2 className="text-xl font-semibold mb-2">📝 퀴즈 응시하기</h2>
          <Form method="post" className="space-y-4">
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
