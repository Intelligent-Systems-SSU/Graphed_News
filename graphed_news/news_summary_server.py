"""
뉴스 요약 gRPC 서버 모듈
"""
import grpc
import asyncio
from concurrent import futures
import sys
import os
import threading

# 현재 디렉토리를 시스템 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# gRPC 관련 모듈 import
from generated import NewsSummary_pb2
from generated import NewsSummary_pb2_grpc

# main 모듈에서 process_news_article 함수 import
from main import process_news_article


loop = asyncio.new_event_loop()

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# 백그라운드 스레드에서 이벤트 루프 실행
threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

class NewsSummaryServicer(NewsSummary_pb2_grpc.NewsSummaryServicer):

    def get(self, request, context):
        """
        gRPC 요청을 처리하는 함수
        
        Args:
            request: NewsSummaryParams 메시지 (URL 포함)
            context: gRPC 컨텍스트
            
        Returns:
            NewsSummaryResult: 요약 결과
        """
        url = request.url
        print(f"요청 받음: URL={url}")
        
        try:
            loop.call_soon_threadsafe(
                lambda: asyncio.create_task(process_news_article(url)).add_done_callback(self.on_done)
            )

            return NewsSummary_pb2.NewsSummaryResult()
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"처리 중 오류 발생: {str(e)}")
            return NewsSummary_pb2.NewsSummaryResult(success=False)

    def on_done(self, future):
        try:
            result = future.result()
            print(f"처리 완료: {result}")
        except Exception as e:
            print(f"오류 발생: {str(e)}")


def serve():
    """
    gRPC 서버를 실행하는 함수
    """
    # 최대 10개의 동시 스레드로 서버 생성
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # 서비스 등록
    NewsSummary_pb2_grpc.add_NewsSummaryServicer_to_server(
        NewsSummaryServicer(), server)
    
    # 서버 포트 설정
    server_address = '[::]:4884'
    server.add_insecure_port(server_address)
    
    # 서버 시작
    server.start()
    print(f"서버가 시작되었습니다. 포트: 4884")
    
    # 서버 실행 유지
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
