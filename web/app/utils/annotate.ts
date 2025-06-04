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
/*                    IMG 무시 + 각주 + 툴팁 주입 함수                 */
/* ------------------------------------------------------------------ */
export function annotateContent(
  rawHtml: string,
  keywords: { keyword: string; description: string }[]
): { annotated: string; refs: RefItem[] } {
  /* 1️⃣ <img> 태그를 토큰으로 치환해 보호 */
  const imgs: string[] = [];
  const htmlWithTokens = rawHtml.replace(/<img\b[^>]*?>/gi, (tag) => {
    const token = `__IMG_TOKEN_${imgs.length}__`;
    imgs.push(tag);
    return token;
  });

  /* 2️⃣ 키워드 위치 탐색 (img 토큰 부분은 공백으로 대체 → 무시) */
  const cleanedHtml = htmlWithTokens.replace(/__IMG_TOKEN_\d+__/g, (m) =>
    " ".repeat(m.length)
  );

  const located: Located[] = [];
  for (const k of keywords) {
    const idx = cleanedHtml
      .toLowerCase()
      .indexOf(k.keyword.toLowerCase());
    if (idx === -1) continue;
    located.push({ ...k, idx, order: 0 });
  }
  if (!located.length)
    return { annotated: rawHtml, refs: [] };

  /* 3️⃣ 등장 순서대로 번호 부여 */
  located.sort((a, b) => a.idx - b.idx);
  located.forEach((k, i) => (k.order = i + 1));

  /* 4️⃣ 본문 치환 (토큰 포함 버전에서 진행) */
  let out = htmlWithTokens;
  for (const { keyword, description, order } of located) {
    const re = new RegExp(`(${escReg(keyword)})`, "i"); // 첫 등장만
    out = out.replace(
      re,
      `$1<sup id="cite-${order}" class="kw-no">` +
        `<a href="#note-${order}" class="kw-ref text-blue-600" ` +
        `data-tooltip-content="${escHtml(description)}">[${order}]</a>` +
      `</sup>`
    );
  }

  /* 5️⃣ 토큰 → 원본 <img> 복원 */
  const annotated = out.replace(/__IMG_TOKEN_(\d+)__/g, (_, idx) => imgs[+idx]);

  /* 6️⃣ refs 배열 생성 */
  const refs: RefItem[] = located.map(({ order, keyword, description }) => ({
    order,
    keyword,
    description,
  }));

  return { annotated, refs };
}
