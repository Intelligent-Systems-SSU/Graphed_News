/* ---------- HTML & RegExp 이스케이프 ---------- */
const escHtml = (s: string) =>
  s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
const escReg = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/* ---------- 타입 ---------- */
export interface RefItem {
  order: number;
  keyword: string;
  description: string;
}
interface Located extends RefItem {
  idx: number;
}

/* ------------------------------------------------------------------ */
/*            <img>·<h1~3> 무시 + 단일 패스 치환 구현                  */
/* ------------------------------------------------------------------ */
export function annotateContent(
  rawHtml: string,
  keywords: { keyword: string; description: string }[]
): { annotated: string; refs: RefItem[] } {
  /* 1️⃣ 보호 대상(IMG + H1/2/3) 토큰 치환 */
  const segs: string[] = [];
  const TOKEN_RE =
    /<img\b[^>]*?>|<h([1-3])[^>]*?>[\s\S]*?<\/h\1>/gi;
  const htmlWithTokens = rawHtml.replace(TOKEN_RE, (m) => {
    const t = `__SEG_TOKEN_${segs.length}__`;
    segs.push(m);
    return t;
  });

  /* 2️⃣ 토큰 → 동일 길이 공백으로 바꾼 사본 → 위치 탐색 */
  const searchable = htmlWithTokens.replace(/__SEG_TOKEN_\d+__/g, (m) =>
    " ".repeat(m.length)
  );

  const located: Located[] = [];
  for (const k of keywords) {
    const hit = searchable
      .toLowerCase()
      .indexOf(k.keyword.toLowerCase());
    if (hit === -1) continue;
    located.push({ ...k, idx: hit, order: 0 });
  }
  if (!located.length) return { annotated: rawHtml, refs: [] };

  /* 3️⃣ 등장 순서 부여 */
  located.sort((a, b) => a.idx - b.idx);
  located.forEach((k, i) => (k.order = i + 1));

  /* 4️⃣ 한 번에 문자열 재조립 (추가 삽입으로 인덱스 어긋남 방지) */
  let cursor = 0;
  let result = "";
  for (const { idx, keyword, order, description } of located) {
    const start = idx;
    const end = idx + keyword.length;
    result += htmlWithTokens.slice(cursor, end); // 키워드 포함 앞부분
    result +=
      `<sup id="cite-${order}" class="kw-no">` +
      `<a href="#note-${order}" class="kw-ref text-blue-600" ` +
      `data-tooltip-content="${escHtml(description)}">[${order}]</a>` +
      `</sup>`;
    cursor = end;
  }
  result += htmlWithTokens.slice(cursor);

  /* 5️⃣ 토큰 복원 */
  const annotated = result.replace(
    /__SEG_TOKEN_(\d+)__/g,
    (_, i) => segs[+i]
  );

  /* 6️⃣ refs 배열 */
  const refs: RefItem[] = located.map(({ order, keyword, description }) => ({
    order,
    keyword,
    description,
  }));

  return { annotated, refs };
}
