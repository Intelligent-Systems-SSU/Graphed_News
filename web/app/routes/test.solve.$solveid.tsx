import { useLoaderData, useActionData, useSubmit, useNavigation } from '@remix-run/react';
import { useNoNavigation } from 'app/components/Navigation';
import createLoader from 'app/utils/createLoader';
import createAction from 'app/utils/createAction';
import { useState, useEffect, useRef } from 'react';

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

export const action = createAction(async ({ db, request, params }) => {
  const formData = await request.formData();
  const intent = formData.get('intent');
  const solveId = params.solveid;

  if (intent === 'complete-test') {
    const correctCount = Number(formData.get('correctCount'));
    const timeElapsed = Number(formData.get('timeElapsed'));

    await db.testSolve.update({
      where: { id: Number(solveId) },
      data: {
        correctAnswers: correctCount,
        time: timeElapsed,
      },
    });

    return { success: true };
  }

  return null;
});

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
  useNoNavigation();
  const { testSolve } = useLoaderData<typeof loader>();
  const actionData = useActionData<typeof action>();
  const submit = useSubmit();
  const formRef = useRef<HTMLFormElement>(null);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<'correct' | 'incorrect' | 'none'>('none');
  const [error, setError] = useState('');
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isTestComplete, setIsTestComplete] = useState(false);
  const [answerMask, setAnswerMask] = useState<number>(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Count number of set bits in the answer mask
  const correctCount = answerMask.toString(2).split('1').length - 1;
  const totalAnswered = currentIndex + 1; // Since we start at index 0
  const accuracy = totalAnswered > 0 ? Math.round((correctCount / totalAnswered) * 100) : 0;

  const question = questions[currentIndex];

  // Timer effect
  useEffect(() => {
    if (!isTestComplete) {
      timerRef.current = setInterval(() => {
        setTimeElapsed((prev) => prev + 1);
      }, 1000);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isTestComplete]);

  // Record test results when completed
  useEffect(() => {
    if (isTestComplete && !actionData?.success) {
      const formData = new FormData();
      formData.append('intent', 'complete-test');
      formData.append('correctCount', answerMask.toString());
      formData.append('timeElapsed', timeElapsed.toString());
      submit(formData, { method: 'post' });
    }
  }, [isTestComplete, correctCount, timeElapsed, submit, actionData]);

  // Check if test is complete
  useEffect(() => {
    if (currentIndex >= questions.length - 1 && result === 'correct') {
      setIsTestComplete(true);
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    }
  }, [currentIndex, result]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  const handleSubmit = () => {
    if (selected === null) {
      setError('답을 체크해주세요.');
      return;
    }
    setError('');
    setSubmitted(true);
    const isCorrect = selected === question.answerIndex;
    setResult(isCorrect ? 'correct' : 'incorrect');

    // Update the bitmask for this answer
    if (isCorrect) {
      setAnswerMask((prev) => prev | (1 << currentIndex));
    }

    // Move to next question or complete test after a delay
    setTimeout(() => {
      if (currentIndex < questions.length - 1) {
        handleNext();
      } else {
        // Submit the form when last question is answered
        const form = formRef.current;
        if (form) {
          form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
        }
        setIsTestComplete(true);
      }
    }, 800);
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex((prev) => prev + 1);
      setSelected(null);
      setSubmitted(false);
      setResult('none');
      setError('');
    } else {
      // Submit the results when last question is answered
      const formData = new FormData();
      formData.append('intent', 'complete-test');
      formData.append('correctCount', answerMask.toString());
      formData.append('timeElapsed', timeElapsed.toString());
      submit(formData, { method: 'post' });
      setIsTestComplete(true);
    }
  };

  if (isTestComplete) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 p-4">
        <div className="w-full max-w-md text-center p-8 bg-white rounded-xl shadow-lg">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">테스트 완료!</h1>
          <p className="text-gray-600 mb-6">
            총 {questions.length}문제 중 {correctCount}문제를 맞추셨습니다.
            <br />
            최종 정답률: <span className="font-semibold">{accuracy}%</span>
          </p>
          <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
            <div
              className="bg-blue-600 h-3 rounded-full transition-all duration-500"
              style={{ width: `${accuracy}%` }}
            />
          </div>
          <a
            href="/"
            className="block w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-center"
          >
            홈으로 돌아가기
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col md:flex-row h-screen">
      {/* Article Section */}
      {/* Article Section */}
      <div className="flex-1 border-r border-gray-200 overflow-hidden flex flex-col">
        <p className="bg-amber-100 p-1 px-2 text-sm">기사를 읽고 문제에 답해주세요.</p>
        <div className="flex-1 overflow-auto">
          {testSolve?.testType === 'A' ? (
            <iframe className="w-full h-full border-0" src="https://graphed-news.pages.dev/article/4" />
          ) : (
            <div className="prose max-w-none p-4 font-normal text-lg ">
              {/* 하드코딩 안내문 및 원문 링크 */}
              <p className="text-sm text-gray-500 mb-3">
                ※ 본 기사는 광고 요소로 인해 모바일 환경에서의 테스트가 어려워 하드코딩 방식으로 삽입되었습니다.
                <br />
                원문 기사는 아래 링크에서 확인하실 수 있습니다:
                <br />
                <a
                  href="https://www.newsis.com/view/NISX20250602_0003199154"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline"
                >
                  https://www.newsis.com/view/NISX20250602_0003199154
                </a>
              </p>
              <h1>달러‑채권 동반 붕괴…포트폴리오 방어 전략은?</h1>
              <div className="border-l-4 border-gray-300 pl-3 ml-2 text-base space-y-0.5 font-bold leading-tight">
                <p>달러-채권 상관관계 붕괴…헤지 수단 무력해져</p>
                <p>美 신용부도스왑프 급등, 재정 위기 우려 현실화</p>
                <p>달러-채권 안전자산 역할 흔들리자 투자자들 포트폴리오 재편 중</p>
              </div>

              <img
                className="mb-1"
                src="https://img1.newsis.com/2025/04/22/NISI20250422_0020781785_web.jpg?rnd=20250422150643"
                alt="서울 중구 하나은행 위변조대응센터에서 직원이 달러화를 정리하는 모습"
              />
              <p className="text-xs text-gray-600 leading-snog">
                [서울=뉴시스] 1일(현지 시간) 파이낸셜타임스에 따르면 지난 4월 도널드 트럼프 대통령의 '해방의 날' 관세
                발표 이후 10년물 국제 수익률은 4.16%에서 4.42%로 상승한 반면, 달러는 주요 통화 대비 4.7% 하락했다. 이로
                인해 미 국채 수익률과 달러 간 상관관계가 최근 3년 내 최저 수준으로 떨어졌다. 사진은 서울 중구 하나은행
                위변조대응센터에서 직원이 달러화를 정리하고 있는 모습.
                <span className="whitespace-nowrap">2025.06.02.</span>
              </p>
              <p>
                [서울=뉴시스]박미선 기자 = 트럼프 행정부의 변화무쌍한 무역 정책으로 미국 자산의 투자 매력이 줄어들면서
                미 국채 수익률과 달러 간 상관관계가 무너지고 있다.
                <br /> <br />
                1일(현지 시간) 파이낸셜타임스에 따르면 지난 4월 도널드 트럼프 대통령의 '해방의 날' 관세 발표 이후 10년물
                국채 수익률은 4.16%에서 4.42%로 상승한 반면, 달러는 주요 통화 대비 4.7% 하락했다. 이로 인해 미 국채
                수익률과 달러 간 상관관계가 최근 3년 내 최저 수준으로 떨어졌다.
                <br /> <br />
                UBS의 G10 외환 전략 책임자 샤합 잘리누스는 "통상적으로 높은 수익률은 미국 경제의 견조함을 뜻하고, 이는
                자본 유입을 유인하는 매력적 요소"라며 "그러나 수익률 상승이 재정 우려나 정책 불확실성에서 비롯된
                것이라면, 달러는 오히려 약세를 보일 수 있다"고 설명했다. 그는 이러한 패턴이 "신흥국 시장에서 더 자주
                보이는 현상"이라고 덧붙였다.
                <br /> <br />
                미 국채 가격의 하방 압력이 강해진 것은 트럼프 대통령의 불확실한 무역정책뿐 아니라 최근 추진 중인 감세
                법안, 글로벌 신용평가사 무디스의 신용등급 강등에 따라 미국의 재정 악화 문제가 수면 위로 떠오른 것이
                영향을 미쳤다.
                <br /> <br />
                이에 미국의 신용부도스와프(CDS) 프리미엄은 최근 그리스와 이탈리아 수준까지 치솟았다. 이는 투자자들이
                미국 정부의 부도 가능성을 재정 위기를 겪은 이들 국가와 비슷하게 보고 있다는 뜻으로, 미국 재정 상황에
                대한 불안감이 커지고 있음을 보여준다.
                <br /> <br />
                여기에 트럼프 대통령의 금리 인하 압박도 투자자들의 불안을 증폭시켰다. 트럼프 대통령은 제롬 파월
                연방준비제도(Fed) 의장 해임론을 거론한 데 이어 최근에는 파월 의장을 백악관으로 불러 "금리를 내리지 않는
                것은 실수"라고 지적했다. 트럼프의 '연준 흔들기'는 미국 자산 매도세를 부추기는 역효과를 낳았다.
                <br /> <br />
                씨타델 증권의 글로벌 금리거래 총책임자 마이클 드 패스는 "달러의 강세는 법치주의, 중앙은행의 독립성, 예측
                가능한 정책 등 제도적 신뢰에서 나온다"며 "지난 3개월간 이런 요소들이 흔들리고 있다"고 말했다. 그는
                "달러의 제도적 신뢰가 훼손되고 있다는 점이 현재 시장의 가장 큰 우려"라고 강조했다.
                <br /> <br />
              </p>
              <div className="border-t border-b border-gray-300 py-2 px-1 mt-4 mb-4 font-bold">
                채권시장 불안과 달러 약세…전문가들 "금, 단기 채권으로 방어 전략 재편해야"
              </div>
              <p>
                미 국채 수익률과 달러 간 상관관계가 깨졌다는 것은 포트폴리오 방어 수단으로서 채권과 달러의 역할이
                무력해졌다는 뜻이다. 투자자들은 시장이 불안할 때 채권, 달러 등 안전자산에 투자하기 마련인데 이들 자산이
                방어 역할을 하지 못하면서, 분산 투자를 통한 포트폴리오 안정 효과가 약해지고 있다.
                <br /> <br />
                아문디의 글로벌 외환 책임자 안드레아스 쾨니히는 "이것은 모든 것을 바꾸는 변화"라며 "지난 몇 년간 달러를
                보유한 것은 포트폴리오의 안정적인 헤지 수단이었지만, 지금처럼 달러가 연동되면, 오히려 포트폴리오의
                리스크를 증가시킨다"고 지적했다. 특히 달러 약세는 달러 자산을 보유한 투자자들이 환율 변동에 따른 손실을
                막기 위해 환 헤지를 강화하면서 달러 매도세가 증가한 것도 영향을 미쳤다. 잘리누스는 "정책 불확실성이
                커질수록 투자자들은 헤지 비중을 더 높이게 된다"며 "만약 기존 달러 자산에 대한 헤지 비율이 높아지면
                수십억 달러 규모의 달러 매도가 발생할 수 있다"고 전망했다.
                <br /> <br />
                이에 골드만삭스는 유로, 엔, 스위스프랑에 대한 달러 약세 흐름이 두드러졌고, 일부 포트폴리오에 금을
                배분하는 것도 효과적인 대응책이라고 제안했다.
                <br /> <br />
                아울러 전문가들은 만기가 짧은 채권을 중심으로 자산을 배분할 것을 조언했다. 장기 채권은 변동성이 확대된
                반면, 단기 및 중기 채권은 비교적 안정적 수익률을 유지하고 있기 때문이다.
                <br /> <br />
                실제 올해 들어 ETF 시장에선 초단기 국채 ETF에 투자 자금이 집중되고 있다. 아이쉐어스와 블룸버그의 3개월
                만기 국채 ETF는 올해 ETF 자금 유입 상위 10위권에 들었고, 총 250억 달러(약 34조원)의 자금을 끌어모았다.
                <br /> <br />
                최근 워런 버핏이 이끄는 버크셔 해서웨이도 단기 국채 보유 비중을 두 배로 늘렸다. JP모건 보고서에 따르면
                버크셔가 보유한 미국 단기 국채 비중은 전체의 5%에 달한다.
                <br /> <br />
                토드 손 스트래터거스 증권 ETF 전략가는 "장기 국채와 장기 회사채는 지난해 9월 이후 모두 마이너스 수익률을
                기록 중"이라며 "금융 위기 이후 처음 있는 일"이라고 말했다.
                <br /> <br />
                조안나 갈레고스 본드블록스 최고경영자(CEO)는 "이런 채권 시장의 불안 속에서, 투자자들이 채권을
                포트폴리오에서 소홀히 다루는 것이 가장 우려스럽다"며 "아직도 너무 많은 이들이 기술주 위주의 지수 ETF에
                중독돼 있다. 두 자릿수 수익률에 익숙해진 것"이라고 지적했다.
                <br /> <br />
                <p>◎공감언론 뉴시스 only@newsis.com</p>
                <div className="text-xs text-gray-500">
                  <p>Copyright © NEWSIS.COM, 무단 전재 및 재배포 금지</p>
                </div>
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Question Section */}
      <div className="md:w-1/3 border-t md:border-t-0 border-gray-200 bg-white flex flex-col">
        <div className="flex-1 overflow-y-auto p-4">
          {/* Question Header */}
          <div className="mb-4">
            <div className="font-medium text-gray-900">{question.title}</div>
            {submitted && result && (
              <div className="mt-1">
                <span className={`text-sm font-medium ${result === 'correct' ? 'text-green-600' : 'text-red-600'}`}>
                  {error || (result === 'correct' ? '정답입니다!' : '틀렸습니다')}
                </span>
              </div>
            )}
          </div>

          {/* Options */}
          <div className="space-y-2 mb-4">
            {question.choices.map((choice, index) => (
              <label
                key={index}
                className={`
                  flex items-center p-2 border rounded cursor-pointer
                  ${selected === index ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}
                  hover:bg-gray-50
                `}
              >
                <input
                  type="radio"
                  name="answer"
                  value={index}
                  checked={selected === index}
                  onChange={() => setSelected(index)}
                  className="h-4 w-4 text-blue-600 mr-2"
                />
                <span className="text-gray-800">{`${index + 1}. ${choice}`}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Action Bar */}
        <div className="border-t border-gray-200 p-3 bg-white">
          <div className="space-y-2">
            {/* Progress and Stats */}
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-500">
                  {currentIndex + 1}/{questions.length}
                </span>
                <span className="text-sm font-medium text-gray-700">{formatTime(timeElapsed)}</span>
              </div>
              <div className="text-sm text-gray-600">
                정답률: <span className="font-medium">{totalAnswered > 0 ? `${accuracy}%` : '0%'}</span>({correctCount}/
                {totalAnswered || 0})
              </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${totalAnswered > 0 ? accuracy : 0}%` }}
              />
            </div>
            {/* Submit Button */}
            <div className="flex justify-end">
              <button
                type="button"
                onClick={handleSubmit}
                disabled={selected === null}
                className={`
                  px-4 py-2 text-sm rounded text-white font-medium
                  ${selected === null ? 'bg-gray-400' : 'bg-blue-600 hover:bg-blue-700'}
                `}
              >
                제출
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
