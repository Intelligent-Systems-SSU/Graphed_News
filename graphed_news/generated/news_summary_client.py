"""
뉴스 요약 gRPC 클라이언트 모듈
"""
import grpc
import argparse
import sys
import os

# 상위 디렉토리의 모듈을 import할 수 있도록 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# gRPC 관련 모듈 import
from generated import NewsSummary_pb2
from generated import NewsSummary_pb2_grpc


def get_news_summary(url, server_address='localhost:4884'):
    """
    gRPC를 통해 뉴스 요약 서비스에 요청을 보내는 함수
    
    Args:
        url (str): 요약할 뉴스 기사 URL
        server_address (str): gRPC 서버 주소 (기본값: localhost:4884)
        
    Returns:
        str: 뉴스 요약 결과
    """
    # gRPC 채널 생성
    with grpc.insecure_channel(server_address) as channel:
        # 클라이언트 스텁 생성
        stub = NewsSummary_pb2_grpc.NewsSummaryStub(channel)
        
        # 요청 메시지 생성
        request = NewsSummary_pb2.NewsSummaryParams(url=url)
        
        try:
            # 서버에 요청 보내기
            print(f"서버에 요청 전송 중: URL={url}")
            response = stub.get(request)
            print("요약 결과 수신 완료")
            
            return response.summary
        except grpc.RpcError as e:
            print(f"gRPC 오류 발생: {e.code()}, {e.details()}")
            return f"오류: {e.details()}"


def main():
    """
    메인 실행 함수
    """
    parser = argparse.ArgumentParser(description="News Summary gRPC Client")
    parser.add_argument("--server", type=str, default="localhost:4884", help="gRPC server address")
    parser.add_argument("--url", type=str, help="URL of the news article to process",
                        default="https://n.news.naver.com/article/082/0001326467")
    args = parser.parse_args()
    # 뉴스 요약 요청
    summary = get_news_summary(args.url, args.server)
    
    # 결과 출력
    print("\n=== 뉴스 요약 결과 ===")
    print(summary)


if __name__ == "__main__":
    main()
