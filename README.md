# LLM 文件处理工具

一个使用大型语言模型（LLM）来处理文件的 Python 项目，目前主要支持通过 LLM 智能批量修改文件名。

## 功能特性

*   **智能文件名修改**：利用 LLM 根据文件内容或原文件名生成更具吸引力或描述性的新文件名。
*   **批量处理**：支持递归处理指定目录下的所有文件。
*   **可配置的 LLM API**：通过 `config.yaml` 文件轻松配置所使用的 LLM API 服务提供商、模型和 API 密钥。

## 环境要求

*   Python 3.x

## 安装步骤

1.  **克隆仓库**：
    ```bash
    git clone <your-repository-url>
    cd LLMFileScript
    ```
2.  **安装依赖**：
    ```bash
    pip install -r requirements.txt
    ```

## 配置说明

项目通过根目录下的 `config.yaml` 文件进行配置。您需要在此文件中提供您的 LLM API 的相关信息。

1.  **创建或修改 `config.yaml` 文件**：
    如果项目根目录下没有 `config.yaml` 文件，请创建一个。如果已存在，请根据您的 LLM 服务提供商信息进行修改。

2.  **配置项**：
    *   `base_config`:
        *   `api_url`: 您的 LLM API 的请求地址。
        *   `api_token`: 您的 LLM API 密钥或访问令牌。
        *   `model_name`: 您希望使用的 LLM 模型名称。
    *   `timeout`: API 请求的超时时间（秒）。

    **示例 `config.yaml`**：
    ```yaml
    base_config:
      api_url: "https://dashscope.aliyuncs.com/compatible-mode/v1/" # 示例 URL，请替换为您的 API URL
      api_token: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" # 请替换为您的 API Token
      model_name: "qwen-max-latest" # 示例模型，请替换为您的模型名称

    # 请求超时时间（秒）
    timeout: 130
    ```
    **重要提示**：请确保 `api_token` 的安全，不要将其提交到公共代码仓库中。建议将 `config.yaml` 文件添加到 `.gitignore` 中（如果尚未添加）。

## 使用方法

目前项目提供了一个主要功能：批量修改文件名。

### 批量修改文件名

使用 `change_filenames` 子命令来批量修改指定目录下的所有文件的名称。

**命令格式**：
```bash
python src/main.py change_filenames <directory_path>
```

**参数说明**：
*   `<directory_path>`：必需参数，指定要处理的包含文件的目录路径。

**示例**：
假设您想修改 `D:\MyDocuments\Reports` 目录下的所有文件名：
```bash
python src/main.py change_filenames D:\MyDocuments\Reports
```
程序将会遍历该目录（包括子目录）下的所有文件，并使用 LLM 为每个文件生成一个新的名称。

## 工作原理（文件名修改）

1.  当执行 `change_filenames` 命令时，`src/main.py` 脚本会解析命令行参数。
2.  它会初始化一个 `APIClient` 实例（来自 `src/llm_api.py`），该实例会从 `config.yaml` 读取 API 配置。
3.  调用 `src/filename_changer.py` 中的 `rename_all_files_in_directory_with_llm` 函数，并传入目标目录和 `APIClient` 实例。
4.  该函数会递归地遍历指定目录中的所有文件。
5.  对于每个文件，会调用 `rename_single_file_with_llm` 函数。
6.  在此函数中，会根据文件的当前名称（不含扩展名的部分）生成一个提示（prompt），要求 LLM 将该名称改为一个更有吸引力且含义相同但表述完全不同的标题。
7.  `APIClient` 将此提示发送给配置的 LLM。
8.  LLM 返回的响应（新的文件名）将被用来重命名文件。

## 项目结构

```
LLMFileScript/
├── .gitignore
├── README.md
├── config.yaml         # LLM API 配置文件
├── requirements.txt    # Python 依赖包列表
├── setup.py            # 项目打包配置文件 (如果需要)
├── src/                # 源代码目录
│   ├── filename_changer.py # 实现文件名修改逻辑
│   ├── llm_api.py        # LLM API 客户端
│   └── main.py           # 命令行接口主程序
└── test_folder/        # (可选) 测试文件存放目录
    └── ...
```

## 未来展望

*   增加更多基于 LLM 的文件处理功能，例如：
    *   文件内容摘要生成
    *   根据文件内容自动分类或打标签
    *   代码文件注释生成或优化
*   支持更多类型的 LLM API 服务商。
*   提供更友好的用户交互界面（例如 Web UI 或桌面应用）。