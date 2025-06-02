import type { MetaFunction } from '@remix-run/cloudflare';
import { Link } from '@remix-run/react';

export const meta: MetaFunction = () => {
  return [
    { title: 'Graphed News' },
    { name: 'description', content: '맥락 중심의 뉴스 이해를 돕는 시각적 뉴스 서비스' },
  ];
};

export default function Index() {
  return (
    <div className="bg-[#f7f7f5] min-h-screen">
      {/* Hero Section */}
      <section className="relative min-h-[900px] w-full overflow-hidden">
        {/* 배경 이미지 */}
        <img
          src="/main-hero.png"
          alt="서비스 시연 이미지"
          loading="lazy"
          onError={(e) => {
            const fallback = '/images/placeholder.jpg';
            if (e.currentTarget.src !== fallback) {
              e.currentTarget.src = fallback;
            }
          }}
          className="absolute inset-0 w-full h-full object-cover opacity-80"
        />

        {/* 어두운 레이어 (텍스트 대비용) */}
        <div className="absolute inset-0 bg-black opacity-20" />

        {/* 오버레이 콘텐츠 */}
        <div className="relative z-10 flex flex-col items-center text-center w-full pt-24 px-4">
          <h1 className="text-4xl md:text-5xl font-bold leading-tight mb-4 drop-shadow-xl">
            <span className="bg-gradient-to-r from-indigo-900 via-blue-500 to-purple-500 bg-[length:200%_100%] bg-clip-text text-transparent animate-gradient">
              뉴스, 더 깊이 있게 이해하자
            </span>
          </h1>
          <p className="text-lg md:text-xl text-white drop-shadow mt-2 mb-6 max-w-2xl">
            SSU KA News는 AI 요약과 시각화를 통해
            <br />
            뉴스의 전후 맥락과 핵심 정보를 한눈에 제공합니다.
          </p>
          <div className="flex gap-4">
            <Link to="/article" className="bg-black text-white py-3 px-6 rounded-full text-lg hover:bg-gray-800">
              시작하기
            </Link>
            <button
              onClick={() => {
                const section = document.getElementById('features');
                section?.scrollIntoView({ behavior: 'smooth' });
              }}
              className="bg-white text-gray-800 py-3 px-6 rounded-full text-lg hover:bg-gray-100"
            >
              자세히 보기
            </button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="bg-white py-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">SSU KA News는 이렇게 작동합니다</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 text-left mt-10">
            <div>
              <h3 className="text-xl font-semibold">🔍 키워드 분석</h3>
              <p className="text-gray-600 mt-2">
                기사의 주요 키워드를 자동 추출하고, 모르는 용어는 간단한 설명과 함께 보여줍니다.
              </p>
            </div>
            <div>
              <h3 className="text-xl font-semibold">📅 타임라인 맥락 제공</h3>
              <p className="text-gray-600 mt-2">
                해당 뉴스 이전과 이후의 흐름을 타임라인으로 정리하여 한눈에 이해할 수 있습니다.
              </p>
            </div>
            <div>
              <h3 className="text-xl font-semibold">📌 5W1H 요약</h3>
              <p className="text-gray-600 mt-2">
                기사에서 핵심 요소(누가, 무엇을, 언제, 어디서, 왜, 어떻게)를 자동 추출하여 보여줍니다.
              </p>
            </div>
            <div>
              <h3 className="text-xl font-semibold">🧠 TMI 포함</h3>
              <p className="text-gray-600 mt-2">
                단순한 사실 외에도 기사를 보며 궁금해질만한 지식 정보를 요약하여 함께 제공합니다.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-[#f0f4f9] py-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">이용하면 이런 변화가 생겨요</h2>
          <ul className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10 text-left text-gray-700">
            <li className="p-6 bg-white rounded-xl shadow">✅ 빠르게 뉴스의 맥락을 이해할 수 있어요</li>
            <li className="p-6 bg-white rounded-xl shadow">✅ 용어에 대한 배경지식이 없어도 쉽게 이해돼요</li>
            <li className="p-6 bg-white rounded-xl shadow">✅ 뉴스 읽는 시간을 절약하면서도 깊이 있는 정보를 얻어요</li>
          </ul>
        </div>
      </section>

      {/* Footer */}
      <footer className="text-center text-sm text-gray-500 py-10">
        © 2025 Graphed News Team. All rights reserved.
      </footer>
    </div>
  );
}
