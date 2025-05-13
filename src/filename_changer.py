from pathlib import Path
from llm_api import APIClient


def rename_single_file_with_llm(file_path: Path, client: APIClient):
    """
    使用LLM处理单个文件的重命名操作（新增异常处理机制）
    
    Args:
        file_path: 文件路径对象
        client: API客户端实例
    """
    try:
        # 生成优化后的标题提示词
        prompt = f'将名称为"{file_path.stem}"的标题改为一个更加有吸引力的标题，要完全不同的标题，但与原标题的含义相同，直接回答新标题即可，防止原作者发现，不要回答无关的内容。'
        new_name = client.ask_llm(prompt)
        new_name = new_name.strip().replace('"', '').replace("'", '').replace('“', '').replace("‘", '').replace("’", '')
        if not new_name:
            raise ValueError('LLM返回空文件名')
        
        new_path = file_path.with_stem(new_name)
        file_path.rename(new_path)
        print(f'成功重命名: {file_path.name} -> {new_path.name}')
    except Exception as e:
        print(f'处理文件 {file_path} 时出错: {str(e)}')
        raise


def rename_all_files_in_directory_with_llm(directory: Path, client: APIClient):
    """
    使用LLM递归处理目录中的所有文件并重命名

    Args:
        directory: 目标目录路径
        client: API客户端实例
    """
    for path in directory.rglob('*'):
        if path.is_file():
            rename_single_file_with_llm(path, client)