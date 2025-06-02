import type { MetaFunction } from '@remix-run/cloudflare';
import React, { useState } from 'react';
import { Link } from '@remix-run/react';

export const meta: MetaFunction = () => {
  return [
    { title: 'SSU KA News' },
    { name: 'description', content: 'AI로 요약된 기사를 확인해 보세요.' }
  ];
};

export default function Index() {
  const articles = [
    {
      id: 1,
      title: '인공지능, 국내 뉴스 산업에 미치는 영향 분석',
      imageUrl: 'https://source.unsplash.com/600x400/?ai,news',
    },
    {
      id: 2,
      title: '숭실대, 새로운 AI 요약 기술 개발',
      imageUrl: 'https://source.unsplash.com/600x400/?university,technology',
    },
    {
      id: 3,
      title: '2025년 상반기 주요 정치 뉴스 요약',
      imageUrl: 'https://source.unsplash.com/600x400/?politics,korea',
    },
    {
      id: 4,
      title: '잘못된 이미지 테스트 (대체 이미지 확인용)',
      imageUrl: 'https://notarealurl.com/image.jpg', // intentionally broken
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-center">📰 SSU KA News</h1>
      <p className="text-gray-600 text-center mb-8">AI로 요약된 뉴스를 간편하게 확인해보세요.</p>

      <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2">
        {articles.map((article) => {
          const [imgError, setImgError] = useState(false);
          return (
            <Link
              key={article.id}
              to={`/article/${article.id}`}
              className="block border rounded-xl overflow-hidden shadow hover:shadow-md transition bg-white"
            >
              {!imgError ? (
                <img
                  src={article.imageUrl}
                  loading="lazy"
                  alt={article.title}
                  onError={() => setImgError(true)}
                  className="w-full h-48 object-cover"
                />
              ) : (
                <div className="w-full h-48 flex items-center justify-center bg-gray-100 text-gray-400">
                  이미지를 불러올 수 없습니다.
                </div>
              )}
              <div className="p-4">
                <h2 className="text-lg font-semibold text-gray-800">{article.title}</h2>
                <p className="text-sm text-blue-500 mt-2">요약 기사 보기 →</p>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
