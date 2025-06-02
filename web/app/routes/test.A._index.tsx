import { Link } from '@remix-run/react';

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
            href="https://example.com/ai-summary-article" // 실제 요약 기사 링크로 바꾸기
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline text-lg"
          >
            요약 기사 바로가기
          </a>
        </div>

        <div>
          <h2 className="text-xl font-semibold mb-2">📝 퀴즈 응시하기</h2>
          <Link
            to="/quiz"
            className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-md text-lg"
          >
            퀴즈 시작
          </Link>
        </div>
      </section>

      <div className="text-sm text-gray-500 mt-10">
        <Link to="/" className="underline hover:text-blue-500">
          ← 홈으로 돌아가기
        </Link>
      </div>
    </div>
  );
}
