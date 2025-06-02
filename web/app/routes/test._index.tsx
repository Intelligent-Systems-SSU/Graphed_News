import { Link } from "@remix-run/react";

export default function TestPage() {
  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">뉴스 기사 테스트 페이지</h1>
      
      <section className="mb-6">
        <h2 className="text-2xl font-semibold">뉴스 요약</h2>
        <p className="mt-2">
          이곳은 선택된 뉴스 기사의 요약이 표시될 영역입니다.
          현재는 테스트용으로 간단한 더미 텍스트를 보여줍니다.
        </p>
      </section>
      
      <section>
        <h2 className="text-2xl font-semibold">문제 출제 영역</h2>
        <p className="mt-2">여기에 문제와 선택지가 표시될 예정입니다.</p>
      </section>
      
      <div className="mt-8">
        <Link to="/" className="text-blue-500 underline">홈으로 돌아가기</Link>
      </div>
    </div>
  );
}
