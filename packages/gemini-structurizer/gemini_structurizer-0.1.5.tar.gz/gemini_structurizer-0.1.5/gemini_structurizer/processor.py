# gemini_structurizer/processor.py

import os
import json
import yaml  # 新增: 用于解析 YAML 配置文件
import argparse
import sys
from google import genai  # 新增: 使用新的 SDK 导入方式
from google.genai import types
def _load_yaml_config(config_path: str) -> dict:
    """
    一个私有辅助函数，用于从给定的路径加载和解析 YAML 文件。
    Args:
        config_path (str): YAML 配置文件的完整路径。
    Returns:
        dict: 解析后的配置内容。
    Raises:
        FileNotFoundError: 如果文件路径不存在。
        yaml.YAMLError: 如果文件内容不是有效的 YAML。
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file not found at path: {config_path}")
        raise
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML configuration file '{config_path}': {e}")
        raise


def get_output_json_path(input_filepath):
    """根据输入文件路径生成输出 JSON 文件的路径。"""
    if not input_filepath:
        return None
    directory = os.path.dirname(os.path.abspath(input_filepath))
    filename = os.path.basename(input_filepath)
    name_part = filename.rsplit('.', 1)[0]
    return os.path.join(directory, name_part + ".json")

def create_config_template(output_path: str, overwrite: bool = False):
    """
    在指定路径创建一个示例 YAML 配置文件模板。

    这个辅助函数可以帮助新用户快速开始。

    Args:
        output_path (str): 想要保存模板文件的路径 (e.g., './config.yaml').
        overwrite (bool, optional): 如果文件已存在，是否覆盖。默认为 False。
    
    Returns:
        bool: 成功创建文件时返回 True，否则返回 False。
    """
    if not overwrite and os.path.exists(output_path):
        print(f"Info: Config file already exists at '{output_path}'. Use overwrite=True to replace it.")
        return False

    template_content = """# Gemini Structurizer Configuration (YAML)
# ==========================================

# (Required) 指定要使用的 Gemini 模型的名称。
# 例如: "gemini-1.5-pro-latest", "gemini-1.5-flash-latest"
model_name: "gemini-2.5-flash-preview-04-17"

# (Optional) 给模型的系统级指令，定义其角色和行为。
system_instruction: "You are an expert in analyzing documents and extracting structured data based on a user-provided JSON schema."

# (Required) 处理文件时给用户的具体指令。
# 你可以使用占位符 {placeholder}, 然后在调用库时通过 template_variables 字典传入实际值。
# {filename} 是一个内置的、永远可用的占位符。
user_prompt_for_file_processing: |
  Please analyze the content of the uploaded file '{filename}'.
  My objective is to extract all the dialogues spoken by '{speaker_name}'.
  Extract the information strictly according to the JSON schema I provided.

# (Required) 期望输出的 JSON 结构的定义。
# 将你的 JSON Schema 作为一个多行字符串直接粘贴在这里。
output_json_schema: |
  {
  "type": "object",
  "properties": {
    "dialogue_list": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "content": {
            "type": "string"
          },
          "id": {
            "type": "integer"
          },
          "non_essential_speech": {
            "type": "boolean"
          },
          "speaker": {
            "type": "string",
            "enum": [
              "Speaker 1",
              "Speaker 2"
            ]
          },
          "topic_id": {
            "type": "integer"
          },
          "content_type": {
            "type": "string",
            "enum": [
              "question",
              "answer",
              "other"
            ]
          }
        },
        "required": [
          "content",
          "id",
          "non_essential_speech",
          "speaker",
          "topic_id",
          "content_type"
        ]
      }
    }
  },
  "required": [
    "dialogue_list"
  ]
}
"""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
        print(f"✔ Successfully created config template at: {os.path.abspath(output_path)}")
        return True
    except IOError as e:
        print(f"❌ Error: Failed to write config template to '{output_path}': {e}")
        return False

def structure_file_with_gemini(
    input_filepath: str,
    config_path: str = None,
    config_data: dict = None,
    api_key: str = None,
    overwrite_existing_output: bool = False,
    template_variables: dict = None
):
    """
    使用 Gemini API 处理指定的文件，并根据提供的配置生成结构化的 JSON。

    Args:
        input_filepath (str): 需要处理的输入文件的路径。
        config_path (str, optional): YAML 配置文件的路径。如果提供了 config_data，则此项将被忽略。
        config_data (dict, optional): 一个包含配置的 Python 字典。如果提供，则优先于 config_path。
        api_key (str, optional): 您的 Google API Key。如果未提供，将尝试从 GOOGLE_API_KEY 环境变量中获取。
        overwrite_existing_output (bool, optional): 如果为 True，即使输出文件已存在，也会重新处理并覆盖。默认为 False。
        template_variables (dict, optional): 用于在 prompt 中渲染占位符的键值对。

    Returns:
        str or None: 成功时返回生成的 JSON 文件的路径，否则返回 None。
    """
    print("--- Gemini File Structurizer ---")

    # 1. 决定配置来源
    if config_data:
        final_config = config_data
        print("Info: Using configuration data provided directly as an argument.")
    elif config_path:
        try:
            final_config = _load_yaml_config(config_path)
            print(f"Info: Loaded configuration from '{os.path.abspath(config_path)}'.")
        except (FileNotFoundError, yaml.YAMLError):
            return None # 错误信息已在 _load_yaml_config 中打印
    else:
        print("Error: Either 'config_path' or 'config_data' must be provided.")
        return None

    # 2. 决定 API Key
    key_to_use = api_key or os.getenv('GOOGLE_API_KEY')
    if not key_to_use:
        print("Error: API Key not provided. Please pass it via the 'api_key' argument or set the GOOGLE_API_KEY environment variable.")
        return None
    
    # 配置客户端
    try:
        client = genai.Client(api_key=key_to_use)
    except Exception as e:
        print(f"Error: Failed to configure or create Gemini client: {e}")
        return None

    # 3. 验证输入文件和输出路径
    if not os.path.exists(input_filepath):
        print(f"Error: Input file '{os.path.abspath(input_filepath)}' not found.")
        return None

    output_json_filepath = get_output_json_path(input_filepath)
    if not output_json_filepath:
        print(f"Error: Could not generate output path for input '{input_filepath}'.")
        return None

    print(f"\nInput file: '{os.path.abspath(input_filepath)}'")
    print(f"Expected output: '{os.path.abspath(output_json_filepath)}'")

    if not overwrite_existing_output and os.path.exists(output_json_filepath):
        print(f"Info: Output file already exists. Skipping processing. Use 'overwrite_existing_output=True' to force.")
        return output_json_filepath

    # 4. 准备 API 调用参数
    try:
        model_name = final_config['model_name']
        system_instruction = final_config.get('system_instruction', '') # system_instruction 是可选的
        user_prompt_template = final_config['user_prompt_for_file_processing']
        
        # 4a. 渲染模板
        if template_variables is None:
            template_variables = {}
        # 确保 filename 占位符总是可用
        template_variables.setdefault('filename', os.path.basename(input_filepath))
        
        user_prompt = user_prompt_template.format(**template_variables)

        # 4b. 解析 JSON Schema (从 YAML 中的字符串)
        schema_str = final_config['output_json_schema']
        output_schema_dict = json.loads(schema_str)

        generation_config = types.GenerateContentConfig(
                        system_instruction =system_instruction if system_instruction else None,
                        responseMimeType = "application/json",
                        responseSchema =  output_schema_dict
                    )
     
    except KeyError as e:
        print(f"Error: Missing required key in configuration: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse 'output_json_schema' as valid JSON: {e}")
        return None

    # 5. 执行 API 调用
    uploaded_file = None
    try:
        print(f"Uploading file: {input_filepath}...")
        uploaded_file = client.files.upload(file=input_filepath)
        print(f"File uploaded successfully as: {uploaded_file.name}")

        print(f"Processing with model: {model_name}...")
        response = client.models.generate_content(
            model=model_name,
            contents=[uploaded_file, user_prompt],
       
            config = generation_config
        )

        output_data = json.loads(response.text)

        os.makedirs(os.path.dirname(output_json_filepath), exist_ok=True)
        with open(output_json_filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"Successfully processed and saved JSON to: {os.path.abspath(output_json_filepath)}")
        return output_json_filepath

    except Exception as e:
        print(f"A critical error occurred during Gemini API processing: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        # 6. 清理上传的文件
        if uploaded_file:
            try:
                print(f"Cleaning up uploaded file: {uploaded_file.name}...")
                client.files.delete(name=uploaded_file.name)
                print("File cleaned up successfully.")
            except Exception as del_e:
                print(f"Warning: Failed to delete uploaded file {uploaded_file.name}: {del_e}")


def main_cli_entry():
    """
    命令行入口点，支持 'init' 和 'run' 两个子命令。
    """
    parser = argparse.ArgumentParser(
        description="A tool to structure files using the Gemini API.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # 子命令解析器
    subparsers = parser.add_subparsers(dest='command', required=True, help='Available commands')

    # --- 'init' 子命令: 用于创建配置文件模板 ---
    parser_init = subparsers.add_parser('init', help='Create a new example YAML config file to get started.')
    parser_init.add_argument(
        '--output',
        default='config.yaml',
        help="Path and filename for the new config file. (default: 'config.yaml' in the current directory)"
    )
    parser_init.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite the config file if it already exists.'
    )

    # --- 'run' 子命令: 用于执行文件处理 ---
    parser_run = subparsers.add_parser('run', help='Run the file structuring process using a config file.')
    parser_run.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the input file to process (e.g., a .txt or .pdf file)."
    )
    parser_run.add_argument(
        "-c", "--config",
        required=True,
        help="Path to the YAML configuration file that defines the processing task."
    )
    parser_run.add_argument(
        "--overwrite",
        action="store_true",
        help="If specified, reprocesses and overwrites the output JSON file even if it already exists."
    )

    args = parser.parse_args()

    # 根据用户选择的子命令执行不同操作
    if args.command == 'init':
        print(f"Attempting to create a new config template at: {os.path.abspath(args.output)}")
        # 调用我们已经写好的 create_config_template 函数
        create_config_template(args.output, args.overwrite)

    elif args.command == 'run':
        print("--- Gemini Structurizer (Run Mode) ---")
        if not os.getenv('GOOGLE_API_KEY'):
            print("\nError: GOOGLE_API_KEY environment variable not set.")
            print("Please set the environment variable before running the command-line tool.")
            print("Example: export GOOGLE_API_KEY='Your-API-Key-Here'")
            sys.exit(1)

        result_path = structure_file_with_gemini(
            input_filepath=args.input,
            config_path=args.config,
            overwrite_existing_output=args.overwrite
        )

        if result_path:
            print(f"\n✔ Processing complete!")
            print(f"Output saved to: {os.path.abspath(result_path)}")
            try:
                with open(result_path, 'r', encoding='utf-8') as f_check:
                    print("\n--- Output JSON Preview ---")
                    json_content = json.load(f_check)
                    print(json.dumps(json_content, indent=2, ensure_ascii=False))
                    print("--------------------------")
            except Exception as e:
                print(f"\nWarning: Could not read or preview the generated JSON file '{result_path}': {e}")
        else:
            print("\n❌ File processing failed or was skipped. Please check the error messages above.")
            sys.exit(1)

    print("\n--- Program End ---")


if __name__ == '__main__':
    main_cli_entry()