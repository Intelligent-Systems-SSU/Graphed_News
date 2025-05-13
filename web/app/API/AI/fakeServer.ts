import grpc from '@grpc/grpc-js';
import { NewsSummaryParams, UnimplementedNewsSummaryService, NewsSummaryResponse } from 'app/generated/NewsSummary';

class FakeServer extends UnimplementedNewsSummaryService {
  get(
    call: grpc.ServerUnaryCall<NewsSummaryParams, NewsSummaryResponse>,
    callback: grpc.sendUnaryData<NewsSummaryResponse>
  ) {
    callback(
      null,
      new NewsSummaryResponse({
        summary: 'This is a fake summary of the news article.',
      })
    );
  }
}

export const fakeServer = new grpc.Server();

export const startFakeServer = () => {
  fakeServer.addService(UnimplementedNewsSummaryService.definition, new FakeServer());
  fakeServer.bindAsync('0.0.0.0:4884', grpc.ServerCredentials.createInsecure(), () => {});
};
