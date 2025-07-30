# promptlib
用于管理prompt, 针对特定项目中特定环节的prompt, 提供 版本管理, 模型适配, 效果调试优化, 便捷使用等能力

使用chainforge 来调整prompt 的进化

未来让大模型自适应去修正

我已经为您创建了 Prompt 管理项目的基础架构和 CLI 工具 [`prompt_manager.py`](prompt_manager.py)，并安装了必要的依赖。

您可以使用以下步骤来使用这个 CLI 工具：

1.  **创建 Prompt 文件:** 创建一个文本文件，例如 [`my_first_prompt.txt`](my_first_prompt.txt)，包含您的 Prompt 模板内容。

    ```
    # my_first_prompt.txt
    你是一个助手，请回答关于 {topic} 的问题。
    问题: {query_str}
    回答:
    ```

2.  **添加 Prompt:** 使用 `add` 命令将 Prompt 添加到管理系统：

    ```bash
    python prompt_manager.py add --name my_first_prompt --version 1.0.0 --description "我的第一个测试 Prompt" --file my_first_prompt.txt --base-class PromptTemplate
    ```

    这将在 `prompts/my_first_prompt/v1.0.0/` 目录下创建 `metadata.yaml` 和 `prompt.txt` 文件。

3.  **列出 Prompt:** 使用 `list` 命令查看已添加的 Prompt：

    ```bash
    python prompt_manager.py list
    ```

4.  **获取 Prompt:** 使用 `get` 命令获取 Prompt 的内容和信息：

    ```bash
    python prompt_manager.py get --name my_first_prompt
    ```

    或者指定版本：

    ```bash
    python prompt_manager.py get --name my_first_prompt --version 1.0.0
    ```

5.  **添加新版本:** 修改现有的 Prompt 文件或创建新的 Prompt 文件，然后使用 `add` 命令添加新版本。

    ```bash
    # 例如，在 my_first_prompt.txt 中添加更多说明
    # my_first_prompt.txt (v1.1.0)
    # 你是一个非常有帮助的助手，请详细回答关于 {topic} 的问题。
    # 问题: {query_str}
    # 回答:

    python prompt_manager.py add --name my_first_prompt --version 1.1.0 --description "添加更多说明" --file my_first_prompt.txt --base-class PromptTemplate
    ```

6.  **删除 Prompt 版本:** 使用 `remove` 命令删除特定版本：

    ```bash
    python prompt_manager.py remove --name my_first_prompt --version 1.0.0
    ```

7.  **删除整个 Prompt:** 使用 `remove` 命令（不指定版本）删除 Prompt 的所有版本：

    ```bash
    python prompt_manager.py remove --name my_first_prompt
    ```

这个项目提供了 Prompt 的版本管理和基本的 CLI 交互功能。您可以根据需要进一步扩展和完善。