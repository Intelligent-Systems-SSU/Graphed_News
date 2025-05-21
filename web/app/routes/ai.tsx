import createAction from 'app/utils/createAction';

export const action = createAction(async ({ db, request }) => {
  const data = (await request.json()) as { newsId: string; summary: string };
  const newsId = Number(data.newsId);
  const summary = data.summary;

  console.log(newsId, summary);

  const news = await db.news.findUnique({ where: { id: newsId } });

  if (!news) {
    throw new Error('News not found');
  }

  await db.newsSummary.upsert({
    where: { newsId: Number(newsId) },
    update: { summary },
    create: { newsId: Number(newsId), summary },
  });

  return new Response(JSON.stringify({ success: true }));
});
