# 🚀 Content Pilot GUI 完整启动指南

**生成时间**: 2026-11-16 20:00 CST  
**目标**: 通过Web界面自动发布内容到多个平台

---

## 📋 准备工作

### 所需工具
- [x] SSH客户端（已配置aliyun别名）
- [x] Python 3.12+
- [x] Node.js v20+
- [x] Playwright浏览器引擎
- [x] ffmpeg视频处理工具

### 服务器信息
```
私有IP: 172.28.194.173
公有IP: 8.155.53.12
SSH别名: aliyun
```

---

## 🔥 完整启动流程（6步）

### Step 1: SSH登录服务器
```bash
ssh aliyun
# 或使用IP:
ssh root@8.155.53.12
```

**预期输出：**
```
Welcome to Alibaba Cloud Elastic Compute Service!
Last login: Mon Nov 16 19:45:00 2026
[root@iZf8z2slk85lm3rcpyn82rZ ~]#
```

---

### Step 2: 进入Content Pilot目录
```bash
cd /opt/content-pilot
ls -la
```

**预期输出：**
```
total 85
drwxr-xr-x  8 root root  4096 Nov 16 17:30 .
drwxr-xr-x 20 root root  4096 Nov 16 17:30 ..
-rw-r--r--  1 root root   123 Nov 16 17:30 .env.example
drwxr-xr-x  6 root root  4096 Nov 16 17:30 .git
drwxr-xr-x  6 root root  4096 Nov 16 17:30 .github
-rw-r--r--  1 root root  1067 Nov 16 17:30 LICENSE
-rw-r--r--  1 root root  5432 Nov 16 17:30 README.md
-rw-r--r--  1 root root   567 Nov 16 17:30 pyproject.toml
drwxr-xr-x  2 root root  4096 Nov 16 17:30 src
drwxr-xr-x  5 root root  4096 Nov 16 17:30 .venv
```

---

### Step 3: 激活虚拟环境
```bash
source .venv/bin/activate
which python
```

**预期输出：**
```
/root/.local/share/uv/python/cpython-3.12.16-linux-x86_64-gnu/bin/python3
```

---

### Step 4: 检查依赖安装状态
```bash
pip list | grep -E 'nicegui|playwright|click'
```

**预期输出：**
```
click          8.1.7
nicegui        1.4.0
playwright     1.40.0
```

如果没有安装，运行：
```bash
pip install -e .
playwright install chromium
```

---

### Step 5: 启动GUI服务
```bash
content-pilot gui --port 8080
```

**预期输出：**
```
╭───────────────────────────────────────────────────╮
│      🚀 Content Pilot v0.1.0 Starting...         │
├───────────────────────────────────────────────────┤
│   Web Interface: http://localhost:8080            │
│   Status: Running                                 │
│   Press Ctrl+C to stop                            │
╰───────────────────────────────────────────────────┘

[NiceGUI] Running on http://0.0.0.0:8080
[INFO] Server started successfully
```

---

### Step 6: 本地访问GUI
在本地浏览器中访问：

**方式A: 端口转发（推荐）**
```bash
# 在另一个终端窗口运行
ssh -N -L 8080:127.0.0.1:8080 aliyun
```

然后打开浏览器访问：`http://localhost:8080`

**方式B: 直接访问（如果服务器开放了8080端口）**
访问：`http://8.155.53.12:8080`

---

## 🎯 GUI界面操作指南

### 首页功能区域

#### 1. Dashboard（仪表盘）
```
┌─────────────────────────────────────────────┐
│  📊 账号状态    │  📝 今日任务    │  📈 数据分析 │
├─────────────────────────────────────────────┤
│  小红书: ✅已登录  │  待发布: 5篇   │  曝光: 0    │
│  知乎:   ✅已登录  │  已发布: 0篇   │  点击: 0    │
│  B站:    ⏳未登录  │  审核中: 2篇   │  转化: 0    │
└─────────────────────────────────────────────┘
```

#### 2. Accounts（账号管理）
```
操作步骤：
1. 点击"添加账号"
2. 选择平台（小红书/知乎/B站/抖音等）
3. 扫描二维码登录
4. 设置账号别名为后续内容标记用
```

#### 3. Content（内容中心）
```
功能模块：
□ AI内容生成器
  - 输入主题 → 选择风格 → 一键生成
  
□ 图片卡片生成
  - 引用风格、标题风格、清单风格、极简风格
  
□ Web图片搜索
  - 集成Unsplash图片库
  
□ 内容编辑器
  - Markdown编辑
  - 实时预览
  - 多平台格式适配
```

#### 4. Publish（发布中心）
```
工作流程：
1. 选择已批准的内容草稿
2. 查看发布预览
3. 确认平台、标签、话题
4. 点击"立即发布"或"定时发布"
5. 查看发布结果和状态
```

#### 5. Schedule（定时任务）
```
设置示例：
┌─────────────────────────────────────┐
│ 任务名称: 每日小红书发布            │
│ 平台: 小红书                        │
│ 时间: 每天 20:00                    │
│ 时区: Asia/Shanghai                 │
│ 内容来源: 自动生成                  │
│ 状态: ✅ 启用                       │
└─────────────────────────────────────┘
```

---

## 💡 高级功能配置

### 配置AI模型
```yaml
# .env文件配置
CP_AI__PROVIDER=qwen           # 千问（推荐国内）
CP_AI__QWEN_API_KEY=sk-xxxx   # 你的API Key

# 或使用其他模型
CP_AI__PROVIDER=openai
CP_AI__OPENAI_API_KEY=sk-xxxx

CP_AI__PROVIDER=claude
CP_AI__ANTHROPIC_API_KEY=sk-ant-xxxx
```

### 配置发布时间
```yaml
# config/default.toml
[schedule]
xiaohongshu_optimal_time = "20:00"
zhihu_optimal_time = "19:00"
bilibili_optimal_time = "18:00"
weibo_optimal_time = "12:00"
```

### 配置安全参数
```yaml
[safety]
max_posts_per_day = 3              # 每天最多发布数
min_interval_minutes = 60          # 最小发布间隔
require_manual_confirm = true      # 需要人工确认
quiet_hours_start = "00:00"       # 静默时段开始
quiet_hours_end = "07:00"         # 静默时段结束
```

---

## 🔧 故障排查

### 问题1: 端口被占用
```
错误信息: Port 8080 already in use
解决方案:
  content-pilot gui --port 8081
```

### 问题2: Playwright浏览器缺失
```
错误信息: Browser not found
解决方案:
  playwright install chromium
```

### 问题3: Python版本过低
```
错误信息: Python 3.11+ required
解决方案:
  /root/.local/bin/uv python install 3.12
  /root/.local/bin/uv venv --python 3.12
```

### 问题4: 二维码不显示
```
可能原因: 
  1. 网络连接问题
  2. Cookie过期
  3. 浏览器缓存

解决方案:
  1. 检查网络连通性
  2. 清除Cookie: rm -rf ~/.config/xhs_cookies/*
  3. 重新登录: content-pilot login --platform xiaohongshu
```

### 问题5: 发布失败
```
错误信息: Publish failed with error code XXXX
排查步骤:
  1. 检查账号登录状态
  2. 验证内容是否符合平台规范
  3. 查看发布日志
  4. 联系平台客服（如有问题）
```

---

## 📊 监控和维护

### 每日检查清单
```bash
# 检查服务状态
ps aux | grep content-pilot

# 查看日志
tail -f /tmp/content_pilot.log

# 检查数据库
sqlite3 /opt/content-pilot/data/content.db "SELECT COUNT(*) FROM posts;"

# 清理临时文件
rm -rf /tmp/content-pilot-temp/*
```

### 每周维护任务
```bash
# 更新项目代码
cd /opt/content-pilot
git pull origin main

# 更新依赖
pip install -e . --upgrade

# 备份数据
cp -r /opt/content-pilot/data /opt/content-pilot/data_backup_$(date +%Y%m%d)

# 检查磁盘空间
df -h /opt
```

---

## 🎉 成功标志

当您看到以下内容时，表示系统已成功启动：

```
✅ Content Pilot GUI running at http://localhost:8080
✅ 3个平台账号已登录
✅ 10条内容已准备好
✅ 定时任务已配置
✅ 实时监控运行中
```

---

> **🚀 祝您使用愉快！**
> 
> **让AI帮您自动化运营社交媒体，释放双手去赚钱！**
> 
> **💰💪🎯**

---

*文档版本: v1.0*  
*最后更新: 2026-11-16 20:00 CST*  
*作者: Agnes AI Assistant*