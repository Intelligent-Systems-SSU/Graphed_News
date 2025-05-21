import createAction from 'app/utils/createAction';

export const action = createAction(async ({ db, request }) => {
  const formData = await request.formData();
  const newsId = formData.get('newsId') as string;
  const summary = formData.get('summary') as string;

  const news = await db.news.findUnique({ where: { id: Number(newsId) } });

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
