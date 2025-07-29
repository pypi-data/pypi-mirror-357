# FastCommit

**AI 生成 Git Commit Message** - 使用大模型自动分析暂存区修改并生成标准的提交信息

## 安装

```bash
pip install fastcommit
```

## 快速开始

### 1. 首次运行配置

第一次运行 `fsc` 时，会自动提示你输入 API 配置信息：

```bash
$ fsc
==================================================
🚀 欢迎使用 FastCommit!
==================================================
首次运行需要配置 API 信息

请输入以下信息:
API Base URL (默认: https://api.deepseek.com/): 
API Key (必填): sk-your-api-key-here
模型名称 (默认: deepseek-reasoner): 
语言 (默认: en): zh

✅ 配置已保存!
📁 配置文件位置: /path/to/python/site-packages/fastcommit/user_config.json
==================================================
```

### 2. 使用

```bash
# 1. 添加文件到暂存区
git add .

# 2. 生成 commit message
fsc

# 3. 查看暂存区状态
fsc --status

# 4. 查看配置
fsc config --show
```

## 💡 使用示例

### 生成 Commit Message

```bash
$ git add src/main.py README.md tests/
$ fsc
正在分析暂存区修改...

修改的文件 (3 个):
  新增: src/main.py
  修改: README.md  
  新增: tests/test_main.py

生成的 Commit Message:
==================================================
feat(main): 添加用户登录功能模块

实现了用户登录验证逻辑，包括：
- 密码加密和安全验证
- 会话管理和状态维护
- 错误处理和用户提示
==================================================

是否使用此消息进行提交？ (y/n/e): y
✅ 提交成功!
```

### 分析历史 Commit

```bash
$ fsc see HEAD~1
正在分析 commit HEAD~1 的修改内容...

Commit: abc123def456
作者: John Doe
日期: 2025-01-15 10:30:00 +0800
原始消息: feat: add user authentication

修改的文件 (3 个):
  新增: src/auth.py
  修改: src/models.py
  新增: tests/test_auth.py

AI 生成的修改总结:
==================================================
## 修改概述
此次提交引入了完整的用户认证系统，为应用程序添加了安全的用户管理功能。

## 主要变更点
1. **新增认证模块** - 创建了 src/auth.py，实现了 JWT token 生成、验证和密码哈希功能
2. **扩展用户模型** - 在 src/models.py 中为 User 模型添加了认证相关字段
3. **完善测试覆盖** - 添加了全面的单元测试确保认证功能的可靠性

## 技术细节
- 使用 JWT 实现无状态认证
- 采用 SHA256 进行密码哈希
- 添加了 24 小时的 token 过期机制

## 影响分析
这是一个关键的安全功能更新，为用户管理奠定了基础，后续可以基于此实现权限控制和会话管理。
==================================================
```

### 使用相对位置

```bash
$ fsc see -1    # 分析上一个commit
$ fsc see -2    # 分析上上个commit
$ fsc see abc123 # 分析指定commit
```

## 配置管理

### 配置文件

配置文件自动保存在 fastcommit 模块安装目录下：`fastcommit/user_config.json`

```json
{
  "api_base": "https://api.deepseek.com/",
  "api_key": "your_api_key_here",
  "model": "deepseek-reasoner",
  "language": "en"
}
```

### 配置选项说明

| 选项名     | 描述                    | 默认值                          |
|-----------|-------------------------|--------------------------------|
| `api_base` | API 基础 URL           | https://api.deepseek.com/      |
| `api_key`  | API 密钥 (必填)        | 无                             |
| `model`    | 使用的模型             | deepseek-reasoner              |
| `language` | 提交信息语言 (zh/en)   | en                             |

### 重新配置

```bash
# 交互式重新配置
fsc config

# 或单独设置某个选项
fsc config --api-key your_new_api_key
fsc config --api-base https://api.openai.com/v1
fsc config --model gpt-4
fsc config --language zh
```

## 📖 命令行选项

```bash
fsc --help                      # 显示帮助信息
fsc --version                   # 显示版本信息
fsc status                      # 显示暂存区文件状态
fsc see <commit>                # 总结指定commit的修改内容
fsc see -1                      # 总结上一个commit
fsc see abc123                  # 总结指定commit号
fsc config                      # 交互式配置
fsc config --show               # 显示当前配置
fsc config --api-key KEY        # 设置 API Key
fsc config --api-base URL       # 设置 API Base URL
fsc config --model MODEL        # 设置模型
fsc config --language LANG      # 设置语言 (zh/en)
```

## 参考

- [DeepSeek](https://deepseek.com) 提供强大的 AI 推理模型
- [OpenAI](https://openai.com) 提供强大的 AI 模型
- [约定式提交](https://www.conventionalcommits.org/zh-hans/) 规范
