import grpc from '@grpc/grpc-js';
import { NewsSummaryClient, NewsSummaryParams } from 'app/generated/NewsSummary';

const getSummaryClient = () =>
  new NewsSummaryClient(import.meta.env.VITE_AI_SERVER_URL, grpc.credentials.createInsecure()); // grpc client를 전역으로 생성하는 것은 금지되어 있습니다. 때문에 매번 생성하여 사용해야 합니다.

export const getSummary = (url: string) => {
  const NewsSummary = getSummaryClient();

  return new Promise<void>((resolve, reject) => {
    NewsSummary.get(
      new NewsSummaryParams({
        url,
      }),
      (error, response) => {
        if (error || !response) {
          reject(error);
        } else {
          resolve();
        }
      }
    );
  });
};
