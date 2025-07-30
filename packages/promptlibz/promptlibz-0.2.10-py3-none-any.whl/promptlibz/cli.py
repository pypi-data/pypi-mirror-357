import argparse
from .core import PromptManager,PromptRepository


# 4. CLI 入口点
def main():
    repository = PromptRepository()
    manager = PromptManager(repository)

    parser = argparse.ArgumentParser(description="Prompt 管理 CLI")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加或更新 Prompt 版本")
    add_parser.add_argument("--name", required=True, help="Prompt 名称")
    add_parser.add_argument("--version", required=True, help="Prompt 版本 (例如: 1.0.0)")
    add_parser.add_argument("--description", default="", help="Prompt 描述")
    add_parser.add_argument("--file", required=True, help="Prompt 模板文件路径")
    add_parser.add_argument("--base-class", required=True, choices=["PromptTemplate", "RichPromptTemplate"], help="基于哪个 LlamaIndex 类")

    # get 命令
    get_parser = subparsers.add_parser("get", help="获取 Prompt 版本")
    get_parser.add_argument("--name", required=True, help="Prompt 名称")
    get_parser.add_argument("--version", help="Prompt 版本 (默认为最新版本)")

    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有可用 Prompt 及其版本")

    # remove 命令
    remove_parser = subparsers.add_parser("remove", help="删除 Prompt 或指定版本")
    remove_parser.add_argument("--name", required=True, help="Prompt 名称")
    remove_parser.add_argument("--version", help="Prompt 版本 (如果未指定，则删除所有版本)")

    args = parser.parse_args()

    if args.command == "add":
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                template_content = f.read()
            manager.add_prompt(args.name, args.version, args.description, template_content, args.base_class)
        except FileNotFoundError:
            print(f"错误: 未找到 Prompt 文件 '{args.file}'")
        except Exception as e:
            print(f"发生错误: {e}")

    elif args.command == "get":
        managed_prompt = manager.get_prompt(args.name, args.version)
        if managed_prompt:
            print(f"--- Prompt: {managed_prompt.name} (版本: {managed_prompt.version}) ---")
            print(f"描述: {managed_prompt.description}")
            print(f"基础类: {managed_prompt.base_class_name}")
            print("\n模板内容:")
            print(managed_prompt._template_content)
            # 示例：如何使用底层的 LlamaIndex Prompt 对象
            # llama_prompt = managed_prompt.get_llama_prompt()
            # print("\n格式化示例 (如果存在变量):")
            # try:
            #     # 假设模板中有变量，例如 "{query_str}"
            #     print(llama_prompt.format(query_str="这是一个测试查询"))
            # except Exception as e:
            #     print(f"无法格式化: {e}")


    elif args.command == "list":
        prompts = manager.list_prompts()
        if not prompts:
            print("未找到任何 Prompt。")
        else:
            print("可用 Prompt:")
            for name, versions in prompts.items():
                print(f"- {name}: {', '.join(versions)}")

    elif args.command == "remove":
        manager.remove_prompt(args.name, args.version)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()