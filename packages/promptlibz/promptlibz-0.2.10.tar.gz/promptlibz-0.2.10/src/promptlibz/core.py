import os
import yaml
import shutil
from llama_index.core import PromptTemplate
from llama_index.core.prompts import RichPromptTemplate

# 1. 自定义 Prompt 类 (使用组合)
# 商品
class BaseManagedPrompt:
    """
    管理 Prompt 的基类，包装 LlamaIndex 的 Prompt 对象。
    """
    def __init__(self, name: str, version: str, description: str, template_content: str, base_class_name: str):
        self.name = name
        self.version = version
        self.description = description
        self._template_content = template_content
        self.base_class_name = base_class_name
        self._llama_prompt_instance = self._create_llama_prompt_instance()

    def _create_llama_prompt_instance(self):
        """根据 base_class_name 创建 LlamaIndex Prompt 实例"""
        if self.base_class_name == "PromptTemplate":
            return PromptTemplate(template=self._template_content)
        elif self.base_class_name == "RichPromptTemplate":
            # RichPromptTemplate 的初始化更复杂，通常需要 PromptTemplate 对象和 template_vars。
            # 为了伪代码的简洁和可运行性，这里简化处理，实际应用需要根据 RichPromptTemplate 的结构调整。
            # 假设这里可以简单地用模板内容初始化，或者包装一个 PromptTemplate。
            # 实际使用时，你可能需要解析更复杂的结构来构建 RichPromptTemplate。
            print("Warning: RichPromptTemplate handling is simplified in this pseudocode.")
            # 实际可能需要更复杂的逻辑来解析 template_content 并构建 RichPromptTemplate
            # 例如：return RichPromptTemplate(template=PromptTemplate(template=self._template_content), template_vars={...})
            return PromptTemplate(template=self._template_content) # 简化为返回 PromptTemplate

        else:
            raise ValueError(f"未知的基础类: {self.base_class_name}")

    def get_llama_prompt(self):
        """获取底层的 LlamaIndex Prompt 对象"""
        return self._llama_prompt_instance

    def format(self, **kwargs):
        """委托格式化操作给底层的 LlamaIndex Prompt"""
        return self._llama_prompt_instance.format(**kwargs)

    def __str__(self):
        return f"ManagedPrompt(name='{self.name}', version='{self.version}', base_class='{self.base_class_name}')"

# 2. Prompt 存储库 (Repository)
class PromptRepository:
    """
    负责 Prompt 的文件系统存储和加载。
    """
    def __init__(self, base_dir="/Users/zhaoxuefeng/GitHub/obsidian/Prompts"):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def _get_prompt_dir(self, name: str) -> str:
        return os.path.join(self.base_dir, name)

    def _get_version_dir(self, name: str, version: str) -> str:
        return os.path.join(self._get_prompt_dir(name), version)

    def _get_metadata_path(self, name: str, version: str) -> str:
        return os.path.join(self._get_version_dir(name, version), "metadata.yaml")

    def _get_prompt_content_path(self, name: str, version: str) -> str:
        return os.path.join(self._get_version_dir(name, version), "prompt.txt")

    def save_prompt(self, name: str, version: str, description: str, template_content: str, base_class_name: str):
        """保存 Prompt 版本"""
        version_dir = self._get_version_dir(name, version)
        os.makedirs(version_dir, exist_ok=True)

        metadata = {
            "name": name,
            "version": version,
            "description": description,
            "base_class": base_class_name
        }
        with open(self._get_metadata_path(name, version), "w", encoding="utf-8") as f:
            yaml.dump(metadata, f)

        with open(self._get_prompt_content_path(name, version), "w", encoding="utf-8") as f:
            f.write(template_content)

    def load_prompt(self, name: str, version: str) -> BaseManagedPrompt | None:
        """加载指定版本的 Prompt"""
        metadata_path = self._get_metadata_path(name, version)
        content_path = self._get_prompt_content_path(name, version)

        if not os.path.exists(metadata_path) or not os.path.exists(content_path):
            return None

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)

        with open(content_path, "r", encoding="utf-8") as f:
            template_content = f.read()

        return BaseManagedPrompt(
            name=metadata["name"],
            version=metadata["version"],
            description=metadata.get("description", ""),
            template_content=template_content,
            base_class_name=metadata["base_class"]
        )

    def list_prompts(self) -> dict[str, list[str]]:
        """列出所有 Prompt 及其版本"""
        prompts = {}
        if not os.path.exists(self.base_dir):
            return prompts

        for name in os.listdir(self.base_dir):
            prompt_dir = self._get_prompt_dir(name)
            if os.path.isdir(prompt_dir):
                versions = []
                for version in os.listdir(prompt_dir):
                    version_dir = self._get_version_dir(name, version)
                if os.path.isdir(version_dir) and os.path.exists(self._get_metadata_path(name, version)):
                    versions.append(version)
                if versions:
                    prompts[name] = sorted(versions) # 按版本号排序
        return prompts

    def delete_prompt_version(self, name: str, version: str) -> bool:
        """删除指定版本的 Prompt"""
        version_dir = self._get_version_dir(name, version)
        if os.path.exists(version_dir):
            shutil.rmtree(version_dir)
            # 如果 Prompt 目录为空，则删除 Prompt 目录
            prompt_dir = self._get_prompt_dir(name)
            if os.path.exists(prompt_dir) and not os.listdir(prompt_dir):
                os.rmdir(prompt_dir)
            return True
        return False

    def delete_prompt(self, name: str) -> bool:
        """删除 Prompt 的所有版本"""
        prompt_dir = self._get_prompt_dir(name)
        if os.path.exists(prompt_dir):
            shutil.rmtree(prompt_dir)
            return True
        return False

# 3. Prompt 管理器 (Manager)
class PromptManager:
    """
    提供 Prompt 管理的高级接口。
    """
    def __init__(self, repository: PromptRepository):
        self.repository = repository

    def add_prompt(self, name: str, version: str, description: str, template_content: str, base_class_name: str) -> bool:
        """添加或更新 Prompt 版本"""
        if not name or not version or not template_content or not base_class_name:
            print("错误: 名称、版本、模板内容和基础类是必需的。")
            return False
        if base_class_name not in ["PromptTemplate", "RichPromptTemplate"]:
             print(f"错误: 无效的基础类 '{base_class_name}'。必须是 'PromptTemplate' 或 'RichPromptTemplate'。")
             return False

        existing_prompt = self.repository.load_prompt(name, version)
        if existing_prompt:
            print(f"警告: Prompt '{name}' 版本 '{version}' 已存在。正在覆盖。")

        self.repository.save_prompt(name, version, description, template_content, base_class_name)
        print(f"Prompt '{name}' 版本 '{version}' 添加/更新成功。")
        return True

    def get_prompt(self, name: str, version: str | None = None) -> BaseManagedPrompt | None:
        """获取 Prompt。如果未指定版本，则获取最新版本。"""
        versions = self.repository.list_prompts().get(name)
        if not versions:
            print(f"错误: 未找到 Prompt '{name}'。")
            return None

        if version is None:
            # 获取最新版本 (假设 sorted() 后最后一个是最新版本)
            latest_version = versions[-1]
            print(f"未指定 Prompt '{name}' 的版本，加载最新版本: '{latest_version}'。")
            return self.repository.load_prompt(name, latest_version)
        else:
            if version not in versions:
                print(f"错误: 未找到 Prompt '{name}' 的版本 '{version}'。可用版本: {', '.join(versions)}")
                return None
            return self.repository.load_prompt(name, version)

    def list_prompts(self) -> dict[str, list[str]]:
        """列出所有 Prompt 及其版本"""
        return self.repository.list_prompts()

    def remove_prompt(self, name: str, version: str | None = None) -> bool:
        """删除 Prompt 或指定版本"""
        if version is None:
            # 删除 Prompt 的所有版本
            success = self.repository.delete_prompt(name)
            if success:
                print(f"Prompt '{name}' 及其所有版本已成功删除。")
            else:
                print(f"错误: 未找到 Prompt '{name}'。")
            return success
        else:
            # 删除指定版本
            success = self.repository.delete_prompt_version(name, version)
            if success:
                print(f"Prompt '{name}' 版本 '{version}' 已成功删除。")
            else:
                print(f"错误: 未找到 Prompt '{name}' 的版本 '{version}'。")
            return success
