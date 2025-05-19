"""
뉴스 요약 gRPC 서버 모듈
"""
import grpc
import asyncio
from concurrent import futures
import sys
import os

# 현재 디렉토리를 시스템 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# gRPC 관련 모듈 import
from generated import NewsSummary_pb2
from generated import NewsSummary_pb2_grpc

# main 모듈에서 process_news_article 함수 import
from main import process_news_article


class NewsSummaryServicer(NewsSummary_pb2_grpc.NewsSummaryServicer):
    def get(self, request, context):
        """
        gRPC 요청을 처리하는 함수
        
        Args:
            request: NewsSummaryParams 메시지 (URL 포함)
            context: gRPC 컨텍스트
            
        Returns:
            NewsSummaryResponse: 요약 결과
        """
        url = request.url
        print(f"요청 받음: URL={url}")
        
        try:
            # 비동기 함수를 동기적으로 실행하기 위한 새 이벤트 루프 생성
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 비동기 함수 실행
            result = loop.run_until_complete(process_news_article(url))
            
            # 이벤트 루프 닫기
            loop.close()
            
            # 처리 결과에서 final_summary 추출
            final_summary = result.get('final_summary', '요약 정보를 찾을 수 없습니다.')
            print(f"처리 완료: {url}")
            
            # 응답 생성
            return NewsSummary_pb2.NewsSummaryResponse(summary=final_summary)
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"처리 중 오류 발생: {str(e)}")
            return NewsSummary_pb2.NewsSummaryResponse(summary=f"오류: {str(e)}")


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