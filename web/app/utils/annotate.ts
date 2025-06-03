/* ---------- 유틸 ---------- */
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

/**
 * - 본문에 <sup><a … data-tooltip-content>[n]</a></sup> 삽입
 * - 하단 주석 목록 렌더용 배열 반환
 */
export function annotateContent(
  html: string,
  list: { keyword: string; description: string }[],
): { annotated: string; refs: RefItem[] } {
  /* 1) 위치 탐색 */
  const located: Located[] = [];
  for (const k of list) {
    const pos = html.toLowerCase().indexOf(k.keyword.toLowerCase());
    if (pos === -1) continue;
    located.push({ ...k, idx: pos, order: 0 });
  }
  if (!located.length) return { annotated: html, refs: [] };

  /* 2) 순서 부여 */
  located.sort((a, b) => a.idx - b.idx);
  located.forEach((k, i) => (k.order = i + 1));

  /* 3) 본문 치환 */
  let out = html;
  for (const { keyword, description, order } of located) {
    const re = new RegExp(`(${escReg(keyword)})`, "i");
    out = out.replace(
      re,
      `$1<sup id="cite-${order}" class="kw-no">` +
        `<a href="#note-${order}" ` +
        `class="kw-ref text-blue-600" ` +
        `data-tooltip-content="${escHtml(description)}">` +
        `[${order}]</a></sup>`,
    );
  }

  /* 4) 하단 주석 배열 */
  const refs: RefItem[] = located.map(({ order, keyword, description }) => ({
    order,
    keyword,
    description,
  }));
  return { annotated: out, refs };
}
