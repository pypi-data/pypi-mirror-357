"""
配置管理模块
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class APIConfig:
    """API 配置类"""

    api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/"
    api_key: str = ""
    model: str = "qwen-plus"
    language: str = "en"


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        # 将配置保存在 fastcommit 模块目录下
        self.config_dir = Path(__file__).parent
        self.config_file = self.config_dir / "user_config.json"

    def load_config(self) -> APIConfig:
        """加载配置"""
        # 从配置文件读取
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    return APIConfig(**config_data)
            except (json.JSONDecodeError, TypeError, KeyError) as e:
                print(f"配置文件格式错误: {e}")
                print("将使用默认配置")

        # 返回默认配置
        return APIConfig()

    def save_config(self, config: APIConfig):
        """保存配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(asdict(config), f, indent=2, ensure_ascii=False)
        except PermissionError:
            print(f"❌ 无法写入配置文件: {self.config_file}")
            print("请检查文件权限或以管理员身份运行")
            raise

    def is_configured(self) -> bool:
        """检查是否已配置"""
        if not self.config_file.exists():
            return False
        config = self.load_config()
        return bool(config.api_key and config.api_key != "")

    def setup_first_time(self) -> APIConfig:
        """首次运行时的配置设置"""
        try:
            print("=" * 50)
            print("🚀 欢迎使用 FastCommit!")
            print("=" * 50)
            print("首次运行需要配置 API 信息")
            print()
            print("支持的 AI 服务提供商:")
            print("1. 通义千问 (Qwen) (推荐)")
            print("   📖 API 文档: https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen")
            print("   💡 API Key 申请: https://bailian.console.aliyun.com/")
            print()
            print("2. DeepSeek")
            print("   📖 API 文档: https://api-docs.deepseek.com/zh-cn/")
            print("   💡 API Key 申请: https://platform.deepseek.com/api_keys")
            print()
            print("3. 自定义")
            print("   💡 配置其他 OpenAI 兼容的 API 服务")
            print()

            # 让用户选择服务提供商
            while True:
                provider = input("请选择服务提供商 (1-通义千问, 2-DeepSeek, 3-自定义): ").strip()
                if provider == "1":
                    # 通义千问配置
                    api_base = "https://dashscope.aliyuncs.com/compatible-mode/v1/"
                    default_model = "qwen-plus"
                    provider_name = "通义千问"
                    api_key_url = "https://bailian.console.aliyun.com/"
                    print("已选择 通义千问")
                    break
                elif provider == "2":
                    # DeepSeek 配置
                    api_base = "https://api.deepseek.com/"
                    default_model = "deepseek-reasoner"
                    provider_name = "DeepSeek"
                    api_key_url = "https://platform.deepseek.com/api_keys"
                    print("已选择 DeepSeek")
                    break
                elif provider == "3":
                    # 自定义配置
                    api_base = ""
                    default_model = ""
                    provider_name = "自定义服务"
                    api_key_url = ""
                    print("已选择 自定义配置")
                    break
                else:
                    print("❌ 无效选择，请输入 1、2 或 3")

            print()
            print("请输入以下信息:")

            # API Base URL (根据选择自动设置，但允许用户修改)
            if provider == "3":
                # 自定义配置需要用户手动输入
                while True:
                    new_api_base = input("API Base URL (必填): ").strip()
                    if new_api_base:
                        api_base = new_api_base
                        break
                    else:
                        print("❌ API Base URL 不能为空，请重新输入")
            else:
                new_api_base = input(f"API Base URL (默认: {api_base}): ").strip()
                if not new_api_base:
                    new_api_base = api_base
                else:
                    api_base = new_api_base

            # API Key
            api_key = ""
            while not api_key:
                if provider == "3":
                    api_key = input("API Key (必填): ").strip()
                    if not api_key:
                        print("❌ API Key 不能为空，请重新输入")
                else:
                    api_key = input(f"{provider_name} API Key (必填): ").strip()
                    if not api_key:
                        print("❌ API Key 不能为空，请重新输入")
                        print(f"💡 请访问 {api_key_url} 申请 API Key")

            # Model
            if provider == "3":
                # 自定义配置需要用户手动输入模型名
                while True:
                    model = input("模型名称 (必填): ").strip()
                    if model:
                        break
                    else:
                        print("❌ 模型名称不能为空，请重新输入")
            else:
                model = input(f"模型名称 (默认: {default_model}): ").strip()
                if not model:
                    model = default_model

            # Language
            language = input(f"语言 (默认: en): ").strip()
            if not language:
                language = "en"

            # 创建配置
            config = APIConfig(api_base=api_base, api_key=api_key, model=model, language=language)

            # 保存配置
            try:
                self.save_config(config)
                print()
                print("✅ 配置已保存!")
                print(f"📁 配置文件位置: {self.config_file}")
                print(f"🎯 使用模型: {provider_name} ({model})")
                print("💡 可以使用 'fsc config' 命令来更新配置")
                print("=" * 50)
                print()
            except Exception as e:
                print(f"❌ 保存配置失败: {e}")
                print("请检查文件权限或以管理员身份运行")
                raise

            return config

        except KeyboardInterrupt:
            print("\n\n👋 配置已取消")
            print("您可以稍后运行 'fsc config' 来配置 API 信息")
            import sys

            sys.exit(0)

    def get_config_info(self) -> Dict:
        """获取配置信息摘要"""
        config = self.load_config()

        return {
            "api_base": config.api_base,
            "model": config.model,
            "language": config.language,
            "api_key_configured": bool(config.api_key),
            "api_key_preview": f"{config.api_key[:8]}..." if config.api_key else "未配置",
            "config_file": str(self.config_file),
        }

    def update_config_interactive(self):
        """交互式更新配置"""
        try:
            config = self.load_config()

            print("当前配置:")
            print(f"  API Base URL: {config.api_base}")
            print(f"  API Key: {config.api_key[:8]}..." if config.api_key else "  API Key: 未设置")
            print(f"  模型: {config.model}")
            print(f"  语言: {config.language}")
            print()

            # API Base URL
            new_base = input(f"新的 API Base URL (当前: {config.api_base}, 回车跳过): ").strip()
            if new_base:
                config.api_base = new_base

            # API Key
            new_key = input(f"新的 API Key (当前: {'已设置' if config.api_key else '未设置'}, 回车跳过): ").strip()
            if new_key:
                config.api_key = new_key

            # Model
            new_model = input(f"新的模型名称 (当前: {config.model}, 回车跳过): ").strip()
            if new_model:
                config.model = new_model

            # Language
            new_language = input(f"新的语言 (当前: {config.language}, 回车跳过): ").strip()
            if new_language:
                config.language = new_language

            # 保存配置
            try:
                self.save_config(config)
                print("✅ 配置已更新!")
            except Exception as e:
                print(f"❌ 更新配置失败: {e}")
                print("请检查文件权限或以管理员身份运行")
                raise

            return config

        except KeyboardInterrupt:
            print("\n\n👋 配置已取消")
            return self.load_config()  # 返回原配置
