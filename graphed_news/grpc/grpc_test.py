import grpc
import generated.NewsSummary_pb2 as NewsSummary_pb2
import generated.NewsSummary_pb2_grpc as NewsSummary_pb2_grpc
from concurrent import futures

class NewsSummaryServicer(NewsSummary_pb2_grpc.NewsSummaryServicer):
    def get(self, request, context):
        # 여기서 요청을 처리하고 응답을 반환합니다.
        summary = f"Summary for URL: {request.url}"
        return NewsSummary_pb2.NewsSummaryResponse(summary=summary)

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    NewsSummary_pb2_grpc.add_NewsSummaryServicer_to_server(NewsSummaryServicer(), server)
    server.add_insecure_port('[::]:4884')
    server.start()
    print("Server started on port 4884")
    server.wait_for_termination()

if __name__ == '__main__':
    run()
