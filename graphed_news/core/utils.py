"""
유틸리티 함수들
"""
import yaml
import os
from typing import Dict, Any


def load_prompt(prompt_file_name: str) -> str:
    """
    YAML 파일에서 프롬프트를 불러오는 범용 함수입니다.
    
    Args:
        prompt_file_name (str): YAML 파일명 (예: 'news_processor_prompt.yaml')
        
    Returns:
        str: 프롬프트 템플릿 (YAML 파일의 첫 번째 값 또는 단일 값)
        
    Raises:
        FileNotFoundError: YAML 파일을 찾을 수 없는 경우
    """
    # prompts 디렉토리 경로 고정
    current_dir = os.path.dirname(__file__)
    prompts_dir = os.path.join(os.path.dirname(current_dir), 'prompts')
    prompt_file_path = os.path.join(prompts_dir, prompt_file_name)
    
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            prompt_data = yaml.safe_load(file)
        
        # 딕셔너리인 경우 첫 번째 값 반환, 아니면 그대로 반환
        if isinstance(prompt_data, dict):
            return list(prompt_data.values())[0]
        else:
            return prompt_data
        
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML 파일 '{prompt_file_path}'를 찾을 수 없습니다.")


def load_model_config(module_name: str) -> Dict[str, Any]:
    """
    config/model_config.yaml에서 특정 모듈의 모델 설정을 불러옵니다.
    
    Args:
        module_name (str): 모듈명 (예: 'news_processor', 'news_qa_generator')
        
    Returns:
        Dict[str, Any]: 모델 설정 딕셔너리
        
    Raises:
        FileNotFoundError: config 파일을 찾을 수 없는 경우
        KeyError: 지정된 모듈 설정을 찾을 수 없는 경우
    """
    # config 디렉토리 경로
    current_dir = os.path.dirname(__file__)
    config_dir = os.path.join(os.path.dirname(current_dir), 'config')
    config_file_path = os.path.join(config_dir, 'model_config.yaml')
    
    try:
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        
        # 모듈별 설정이 있으면 반환, 없으면 기본 설정 반환
        if module_name in config_data.get('models', {}):
            return config_data['models'][module_name]
        elif 'default' in config_data:
            return config_data['default']
        else:
            raise KeyError(f"모듈 '{module_name}' 설정과 기본 설정을 찾을 수 없습니다.")
            
    except FileNotFoundError:
        raise FileNotFoundError(f"config 파일 '{config_file_path}'를 찾을 수 없습니다.")