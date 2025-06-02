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
      <section className="text-center px-6 py-20 max-w-5xl mx-auto">
        <h1 className="text-4xl font-bold leading-tight mb-4">
          <span className="text-gradient bg-gradient-to-r from-green-400 via-blue-500 to-pink-500 text-transparent bg-clip-text">
            뉴스, 더 깊이 있게 이해하자
          </span>
        </h1>
        <p className="text-lg text-gray-700 mb-8">
          SSU KA News는 AI 요약과 시각화를 통해
          <br />
          뉴스의 전후 맥락과 핵심 정보를 한눈에 제공합니다.
        </p>
        <div className="flex justify-center gap-4">
          <Link to="/article" className="bg-black text-white py-3 px-6 rounded-full text-lg hover:bg-gray-800">
            시작하기
          </Link>
          <a
            href="#features"
            className="border border-gray-400 text-gray-700 py-3 px-6 rounded-full text-lg hover:bg-gray-100"
          >
            자세히 보기
          </a>
        </div>
        <img
          src="/hero-graphic.png"
          alt="서비스 시연 이미지"
          loading="lazy"
          onError={(e) => {
            const fallback = '/images/placeholder.jpg';
            if (e.currentTarget.src !== fallback) {
              e.currentTarget.src = fallback;
            }
          }}
          className="mt-12 mx-auto max-w-full rounded-xl shadow-xl"
        />
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
