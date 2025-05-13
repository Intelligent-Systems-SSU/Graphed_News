import grpc from '@grpc/grpc-js';
import { NewsSummaryClient, NewsSummaryParams } from 'app/generated/NewsSummary';

const getSummaryClient = () => new NewsSummaryClient('localhost:4884', grpc.credentials.createInsecure()); // grpc client를 전역으로 생성하는 것은 금지되어 있습니다. 때문에 매번 생성하여 사용해야 합니다.

export const getSummary = () => {
  const NewsSummary = getSummaryClient();

  return new Promise((resolve, reject) => {
    NewsSummary.get(
      new NewsSummaryParams({
        url: 'https://example.com/news-article',
      }),
      (error, response) => {
        if (error || !response) {
          reject(error);
        } else {
          resolve(response.summary);
        }
      }
    );
  });
};
