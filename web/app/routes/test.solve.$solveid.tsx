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
      <div className="flex-1 border-r border-gray-200 overflow-hidden flex flex-col">
        <p className="bg-amber-100 p-1 px-2 text-sm">기사를 읽고 문제에 답해주세요.</p>
        <div className="flex-1 overflow-auto">
          <iframe
            className="w-full h-full border-0"
            src={
              testSolve?.testType === 'A'
                ? 'https://graphed-news.pages.dev/article/4'
                : 'https://www.newsis.com/view/NISX20250602_0003199154'
            }
          />
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
