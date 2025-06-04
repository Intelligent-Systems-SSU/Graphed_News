import { Link } from "@remix-run/react";
import { useState } from "react";

type Question = {
  title: string;
  choices: string[];
  answerIndex: number;
};

const questions: Question[] = [
  {
    title: "다음 중 기사 요약의 핵심 내용으로 적절한 것은?",
    choices: [
      "경제 성장률은 작년보다 낮아졌다.",
      "기사는 정치인의 발언을 중심으로 작성되었다.",
      "해당 정책은 실질적 효과가 입증되었다.",
      "정부는 보조금 정책을 철회했다.",
    ],
    answerIndex: 2,
  },
  {
    title: "기사에서 언급된 정책의 주요 대상은 누구인가?",
    choices: [
      "청년 창업가",
      "중소기업",
      "대기업",
      "공공기관 직원",
    ],
    answerIndex: 2,
  },
  {
    title: "정책 효과를 뒷받침하는 근거로 언급된 것은?",
    choices: [
      "정부 보고서",
      "여론 조사 결과",
      "전문가 인터뷰",
      "현장 사례 분석",
    ],
    answerIndex: 2,
  },
];

export default function TestPage() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<"correct" | "incorrect" | "none">("none");
  const [error, setError] = useState("");

  const question = questions[currentIndex];

  const handleSubmit = () => {
    if (selected === null) {
      setError("답을 체크해주세요.");
      return;
    }

    setError("");
    setSubmitted(true);

    if (selected === question.answerIndex) {
      setResult("correct");
    } else {
      setResult("incorrect");
    }
  };

  const handleNext = () => {
    setCurrentIndex((prev) => prev + 1);
    setSelected(null);
    setSubmitted(false);
    setResult("none");
    setError("");
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-6">뉴스 기사 테스트 문제</h1>

      <section className="bg-white rounded-lg shadow p-6">
        {/* 상단 타이틀 + 결과 메시지 위치 */}
        <div className="flex items-center justify-between mb-4">
          <div className="text-xl font-semibold">
            <span className="text-gray-500 font-bold mr-4">문제 {currentIndex + 1}</span>
            {question.title}
          </div>

          {/* 정답 / 오답 / 미선택 메시지 */}
          {(result === "correct" || result === "incorrect" || error) && (
            <span
              className={`font-semibold whitespace-nowrap ${
                result === "correct"
                  ? "text-green-600"
                  : result === "incorrect"
                  ? "text-red-600"
                  : "text-red-500"
              }`}
            >
              {error || (result === "correct" ? "맞았습니다" : "틀렸습니다")}
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
            {(!submitted || result === "incorrect") && (
              <button
                type="button"
                onClick={handleSubmit}
                className="bg-blue-600 text-white px-5 py-2 rounded hover:bg-blue-700"
              >
                제출
              </button>
            )}
            <div className="flex-1"></div>
            {submitted && result === "correct" && currentIndex < questions.length - 1 && (
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
  );
}
