import { useLoaderData } from '@remix-run/react';
import createLoader from 'app/utils/createLoader';
import { useState } from 'react';

type Question = {
  title: string;
  choices: string[];
  answerIndex: number;
};

const questions: Question[] = [
  {
    title: "트럼프 대통령의 '해방의 날' 관세 발표 이후, 미 국채 수익률과 달러는 각각 어떻게 변했는가?",
    choices: [
      '국채 수익률 상승, 달러 강세',
      '국채 수익률 하락, 달러 약세',
      '국채 수익률 상승, 달러 약세',
      '국채 수익률 하락, 달러 강세',
    ],
    answerIndex: 2,
  },
  {
    title: "다음 중 기사에서 언급된 '달러 약세'의 원인으로 가장 거리가 먼 것은 무엇인가요?",
    choices: [
      '트럼프 행정부의 예측 불가능한 무역 정책과 연준 압박',
      '달러 자산 보유자들의 환 헤지(Hedge) 강화 움직임',
      '미국 정부의 재정 악화에 대한 시장의 우려',
      '견고한 미국 경제 성장률에 따른 인플레이션 압력',
    ],
    answerIndex: 3,
  },
  {
    title: '최근 미국의 신용부도스와프(CDS) 프리미엄이 치솟았다는 것은 무엇을 의미하나요?',
    choices: [
      '미국 국채가 전 세계에서 가장 안전한 자산임을 재확인시켜 준다.',
      '미국 달러가 기축통화의 지위를 상실했음을 보여주는 결정적 증거이다.',
      '미국이 그리스, 이탈리아와 동일한 수준의 절대적 부도 위험에 처했음을 의미한다.',
      '미국의 재정 상황에 대한 시장의 불안감이 커지고 있음을 보여준다.',
    ],
    answerIndex: 3,
  },
  {
    title: "기사에서 사용된 '헤지(hedge)'의 의미로 가장 적절한 것은?",
    choices: [
      '투자 수익을 최대화하기 위한 고수익 자산 집중 전략',
      '특정 자산에만 투자하여 변동성을 줄이는 집중 투자 기법',
      '환율이나 금리 등 외부 요인에 따른 손실을 줄이기 위한 위험 회피 전략',
      '리스크가 큰 자산을 피하기 위해 현금을 보유하는 전략',
    ],
    answerIndex: 2,
  },
];

export const loader = createLoader(async ({ db, params }) => {
  const solveId = params.solveid;

  const testSolve = await db.testSolve.findUnique({
    where: {
      id: Number(solveId),
    },
  });

  return { testSolve };
});

export default function TestPage() {
  const { testSolve } = useLoaderData<typeof loader>();

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<'correct' | 'incorrect' | 'none'>('none');
  const [error, setError] = useState('');

  const question = questions[currentIndex];

  const handleSubmit = () => {
    if (selected === null) {
      setError('답을 체크해주세요.');
      return;
    }

    setError('');
    setSubmitted(true);

    if (selected === question.answerIndex) {
      setResult('correct');
    } else {
      setResult('incorrect');
    }
  };

  const handleNext = () => {
    setCurrentIndex((prev) => prev + 1);
    setSelected(null);
    setSubmitted(false);
    setResult('none');
    setError('');
  };

  return (
    <div className="flex grow-1 md:flex-row flex-col">
      <div className="grow-1 h-auto border border-gray-300 rounded flex flex-col">
        <p className="bg-amber-100 p-1 px-2">기사를 읽고 문제에 답해주세요.</p>
        <iframe
          className="w-full grow-1"
          src={
            testSolve?.testType === 'A'
              ? 'https://graphed-news.pages.dev/article/4'
              : 'https://www.newsis.com/view/NISX20250602_0003199154'
          }
        />
      </div>
      <div className="max-w-xl md:sticky md:bottom-0">
        <section className="bg-white p-3">
          {/* 상단 타이틀 + 결과 메시지 위치 */}
          <div className="flex items-center justify-between">
            <div className="text-xl font-semibold">
              <span className="text-gray-500 font-bold mr-4">문제 {currentIndex + 1}</span>
              {question.title}
            </div>

            {/* 정답 / 오답 / 미선택 메시지 */}
            {(result === 'correct' || result === 'incorrect' || error) && (
              <span
                className={`font-semibold whitespace-nowrap ${
                  result === 'correct' ? 'text-green-600' : result === 'incorrect' ? 'text-red-600' : 'text-red-500'
                }`}
              >
                {error || (result === 'correct' ? '맞았습니다' : '틀렸습니다')}
              </span>
            )}
          </div>

          {/* 보기 영역 */}
          <form className="space-y-4">
            {question.choices.map((choice, index) => (
              <div key={index} className="flex items-center">
                <input
                  type="radio"
                  id={`option${index}`}
                  name="answer"
                  value={index}
                  checked={selected === index}
                  onChange={() => setSelected(index)}
                  className="mr-2"
                />
                <label htmlFor={`option${index}`}>{`${index + 1}. ${choice}`}</label>
              </div>
            ))}

            {/* 제출 & 다음 버튼을 좌우에 나누어 정렬 */}
            <div className="mt-6 flex justify-between items-center">
              {(!submitted || result === 'incorrect') && (
                <button
                  type="button"
                  onClick={handleSubmit}
                  className="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700"
                >
                  제출
                </button>
              )}
              <div className="flex-1"></div>
              {submitted && result === 'correct' && currentIndex < questions.length - 1 && (
                <button
                  type="button"
                  onClick={handleNext}
                  className="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700"
                >
                  다음
                </button>
              )}
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
