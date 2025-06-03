import createAction from 'app/utils/createAction';

export const action = createAction(async ({ db, request }) => {
  const data = (await request.json()) as {
    newsId: string;
    summary: string;
    keyword: { keyword: string; description: string }[];
  };
  const newsId = Number(data.newsId);
  const summary = data.summary;
  const keywords = data.keyword;

  const news = await db.news.findUnique({ where: { id: newsId } });

  if (!news) {
    throw new Error('News not found');
  }

  await db.newsSummary.upsert({
    where: { newsId },
    update: { summary },
    create: { newsId, summary },
  });

  await db.newsKeyword.deleteMany({ where: { newsId } });

  for (const keyword of keywords) {
    await db.newsKeyword.create({
      data: {
        newsId,
        keyword: keyword.keyword,
        description: keyword.description,
      },
    });
  }

  return new Response(JSON.stringify({ success: true }));
});
