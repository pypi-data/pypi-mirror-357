# Git AI Commit 升级指南

本指南介绍如何将 Git AI Commit 工具升级到最新版本。

## 🔍 检查当前版本

首先检查您当前安装的版本：

```bash
git-ai-commit-gui --help
```

或者在GUI界面中查看版本信息。

## 🚀 升级方法

### 方法1：使用 uv tool (推荐)

如果您是通过 `uv tool install` 安装的：

```bash
# 升级到最新版本
uv tool upgrade git-ai-commit-gui

# 验证升级结果
git-ai-commit-gui --help
```

**如果升级失败，可以尝试重新安装：**
```bash
# 卸载旧版本
uv tool uninstall git-ai-commit-gui

# 安装最新版本
uv tool install git-ai-commit-gui
```

### 方法2：使用 pip

如果您是通过 `pip install` 安装的：

```bash
# 升级到最新版本
pip install --upgrade git-ai-commit-gui

# 验证升级结果
git-ai-commit-gui --help
```

**如果升级失败，可以尝试强制重新安装：**
```bash
# 强制重新安装
pip install --force-reinstall git-ai-commit-gui
```

### 方法3：从源码升级

如果您是从GitHub源码安装的：

```bash
# 进入项目目录
cd ai_git_commit_gui

# 拉取最新代码
git pull origin main

# 使用uv更新依赖
uv sync

# 或者使用pip重新安装
pip install -e .
```

## ✅ 验证升级

升级完成后，验证新版本是否正常工作：

```bash
# 检查版本信息
git-ai-commit-gui --help

# 测试基本功能
git-ai-commit-gui --auto
```

## 🔧 升级故障排除

### 问题1：升级后命令找不到

**解决方案：**
```bash
# 重新安装
uv tool uninstall git-ai-commit-gui
uv tool install git-ai-commit-gui

# 或者检查PATH环境变量
echo $PATH
```

### 问题2：依赖冲突

**解决方案：**
```bash
# 清理缓存
pip cache purge

# 重新安装
pip uninstall git-ai-commit-gui
pip install git-ai-commit-gui
```

### 问题3：配置文件兼容性

新版本可能会更新配置文件格式。如果遇到配置问题：

```bash
# 备份现有配置
cp ~/.git_ai_commit/config.json ~/.git_ai_commit/config.json.backup

# 删除配置文件，让程序重新生成
rm ~/.git_ai_commit/config.json

# 重新启动程序并重新配置
git-ai-commit-gui
```

## 📋 版本更新日志

### v0.2.0 (最新)
- 功能改进和性能优化
- 修复已知问题
- 更新依赖版本

### v0.1.1
- 初始稳定版本
- 基础功能完善

## 🆘 获取帮助

如果升级过程中遇到问题：

1. **查看错误日志**：注意升级过程中的错误信息
2. **检查系统要求**：确保Python版本 >= 3.12
3. **提交Issue**：在GitHub仓库提交问题报告
4. **联系支持**：发送邮件至开发者邮箱

## 📞 联系方式

- GitHub Issues: https://github.com/duolabmeng6/ai_git_commit_gui/issues
- 开发者邮箱: 1715109585@qq.com

---

⚠️ **重要提示**：升级前建议备份重要的配置文件和数据。
