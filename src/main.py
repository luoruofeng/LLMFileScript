import argparse
from pathlib import Path
from llm_api import APIClient
from filename_changer import rename_all_files_in_directory_with_llm
import sys

def main():
    """
    命令行主函数（新增change_filenames子命令）
    """
    parser = argparse.ArgumentParser(description='LLM文件处理工具')
    subparsers = parser.add_subparsers(dest='command')
    
    # 文件名修改命令
    rename_parser = subparsers.add_parser('change_filenames', help='批量修改文件名')
    rename_parser.add_argument('directory', type=str, help='要处理的目录路径')
    
    # 命令执行逻辑
    args = parser.parse_args()
    if args.command == 'change_filenames':
        client = APIClient()
        target_dir = Path(args.directory)
        try:
            rename_all_files_in_directory_with_llm(target_dir, client)
        except Exception as e:
            print(f'\n错误: {str(e)}')
            print('已中止文件重命名操作，未修改任何文件名')
            sys.exit(1)
    else:
        print("Hello from Python Project!")

if __name__ == "__main__":
    main()