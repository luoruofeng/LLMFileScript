import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError # 导入OpenAI库及特定异常类型

class APIClient:
    """
    大模型API请求客户端, 使用与OpenAI兼容的接口 (例如阿里云百炼DashScope)。

    Attributes:
        config_path (str): 配置文件的路径。
        client (OpenAI): OpenAI API 客户端实例。
    """

    def __init__(self, config_path: str = None):
        """
        初始化APIClient。

        Args:
            config_path (str, optional): 配置文件的路径。
                                         如果未提供，则默认为项目根目录下的 'config.yaml'。
        """
        self.config = self._load_config(config_path or str(Path(__file__).resolve().parent.parent / 'config.yaml'))
        
        # 从配置中获取 api_key 和 base_url
        # 优先使用配置文件中的 api_token
        api_key = self.config['base_config'].get('api_token')
        if not api_key:
            # 如果配置文件中没有，则尝试从环境变量 DASHSCOPE_API_KEY 获取
            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                # 如果两者都未配置，可以记录一个警告或在后续操作中依赖OpenAI库自身处理
                print("警告: API Key 未在配置文件或环境变量 DASHSCOPE_API_KEY 中找到。API调用可能会失败。")

        # 获取 base_url，如果配置中没有，则使用示例中的默认值
        base_url = self.config['base_config'].get('api_url', "https://dashscope.aliyuncs.com/compatible-mode/v1")

        # 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )

    def _load_config(self, path: str) -> Dict[str, Any]:
        """
        加载YAML配置文件。

        Args:
            path (str): 配置文件路径。

        Returns:
            Dict[str, Any]: 配置字典。
        """
        # 使用 resolve()确保路径是绝对的，并规范化
        config_file_path = Path(path).resolve()
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"错误: 配置文件未找到于路径 {config_file_path}")
            # 可以考虑抛出自定义异常或返回默认配置
            raise
        except yaml.YAMLError as e:
            print(f"错误: 解析配置文件 {config_file_path} 失败: {e}")
            # 同上
            raise

    def ask_llm(self, prompt: str, model_name: str = None, 
               temperature: float = 0.7, max_tokens: int = 200) -> Optional[str]:
        """
        向大模型发送请求并获取响应。

        Args:
            prompt (str): 用户输入的提示。
            model_name (str, optional): 模型名称。如果未提供，则使用配置文件中的默认模型。
                                        如果配置文件中也没有，则默认为 'qwen-plus'。
            temperature (float, optional): 控制生成文本的随机性，值越高越随机。默认为 0.7。
            max_tokens (int, optional): 生成文本的最大长度（token数）。默认为 200。

        Returns:
            Optional[str]: 模型的响应文本。如果请求失败或无有效响应，则返回None或错误信息字符串。
        """
        # 获取实际使用的模型名称
        # 优先使用传入的 model_name，其次是配置文件中的 model_name，最后是默认值 'qwen-plus'
        actual_model_name = model_name or self.config['base_config'].get('model_name', 'qwen-plus')

        # 构建发送给API的消息列表
        messages = [
            {"role": "system", "content": "You are a helpful assistant."}, # 系统消息，定义助手的角色
            {"role": "user", "content": prompt}, # 用户消息，包含具体的请求内容
        ]

        try:
            # 调用OpenAI兼容的API
            completion = self.client.chat.completions.create(
                model=actual_model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                # extra_body={"enable_thinking": False} # 根据用户提供的demo，特定模型（如Qwen3）可能需要此参数。
                                                        # 为保持通用性，默认注释掉。如果需要，可以从配置或参数传入。
            )
            
            # 调试时可以取消注释下一行，打印完整的API响应
            # print(completion.model_dump_json()) 

            # 解析响应
            if completion.choices and len(completion.choices) > 0:
                message = completion.choices[0].message
                if message and message.content:
                    return message.content.strip() # 返回模型生成的文本内容，并去除首尾空白
                else:
                    print("错误：模型响应的choice中不包含有效的message content。")
                    return "模型响应数据格式异常：message content为空"
            else:
                print(f"错误：模型 '{actual_model_name}' 未返回有效的choices。响应: {completion}")
                return "模型响应异常：未返回choices"
        
        # OpenAI Python SDK v1.0.0+ 推荐的异常处理方式
        except AuthenticationError as e:
            error_msg = e.message if hasattr(e, 'message') and e.message else str(e)
            print(f"API认证失败: {error_msg}")
            # DashScope的错误信息可能在 e.body['message']
            error_detail = e.body.get('message') if hasattr(e, 'body') and isinstance(e.body, dict) else error_msg
            return f"API认证失败: {error_detail}"
        except RateLimitError as e:
            error_msg = e.message if hasattr(e, 'message') and e.message else str(e)
            print(f"API请求频率超限: {error_msg}")
            error_detail = e.body.get('message') if hasattr(e, 'body') and isinstance(e.body, dict) else error_msg
            return f"API请求频率超限: {error_detail}"
        except APIConnectionError as e:
            error_msg = e.message if hasattr(e, 'message') and e.message else str(e)
            print(f"无法连接到API: {error_msg}")
            return "无法连接到API，请检查网络或API服务器地址"
        except APIError as e: # 更通用的API错误 (例如 4xx, 5xx 错误)
            status_code = e.status_code if hasattr(e, 'status_code') else 'N/A'
            error_msg = e.message if hasattr(e, 'message') and e.message else str(e)
            print(f"API返回错误 (状态码 {status_code}): {error_msg}")
            # 尝试从 e.body 或 e.response 获取更详细的错误信息
            error_detail = error_msg
            if hasattr(e, 'body') and isinstance(e.body, dict) and 'message' in e.body:
                error_detail = e.body['message']
            elif hasattr(e, 'response') and hasattr(e.response, 'text'):
                 try:
                    error_json = e.response.json()
                    if 'message' in error_json:
                        error_detail = error_json['message']
                    elif 'code' in error_json: # DashScope specific
                         error_detail = f"Code: {error_json['code']}, Message: {error_json.get('message', '')}"
                 except ValueError: # Not JSON
                    error_detail = e.response.text[:200] # Truncate if too long
            return f"API请求失败: {error_detail}"
        except Exception as e: # 其他所有未捕获的Python异常
            print(f"调用LLM时发生未知错误: {type(e).__name__} - {str(e)}")
            return f"调用LLM时发生未知错误: {str(e)}"