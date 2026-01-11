# Python环境设置指南

## 当前环境要求

⚠️ **重要提示**：本项目需要使用 **Python 3.12**（或 3.11），因为以下依赖包尚不支持 Python 3.13：
- `asyncpg`: 编译时出现Python 3.13 API兼容性问题
- `pydantic-core`: Python 3.13中ForwardRef API变更导致编译失败

**推荐使用 Python 3.12**，已测试通过。

### 检查Python版本

```bash
python3.12 --version  # 应该显示 Python 3.12.x
```

如果系统没有Python 3.12，可以通过Homebrew安装：

```bash
brew install python@3.12
```

## 环境管理方案选择

### 方案1：使用venv（Python内置，推荐）⭐

**优点**：
- ✅ Python内置，无需额外安装
- ✅ 轻量级，启动快
- ✅ 完全隔离项目依赖
- ✅ 适合大多数项目

**缺点**：
- ❌ 不提供Python版本管理

**适用场景**：当前项目只需要Python 3.12，不需要管理多个Python版本

### 方案2：使用conda/miniconda

**优点**：
- ✅ 可以管理多个Python版本
- ✅ 提供科学计算包（NumPy、SciPy等）
- ✅ 更强大的包管理（二进制包）
- ✅ 跨平台支持好

**缺点**：
- ❌ 需要额外安装（约400MB）
- ❌ 启动较慢
- ❌ 对于Web项目可能过于复杂

**适用场景**：需要管理多个Python版本，或需要科学计算包

## 推荐方案：使用venv

对于当前的词典查询服务项目，**推荐使用venv**，原因：
1. 项目只依赖标准Web框架（FastAPI、asyncpg等）
2. 不需要科学计算包
3. Python 3.12已满足需求（Python 3.13存在兼容性问题）
4. 更轻量级、启动更快

## 使用venv设置环境

### 1. 创建虚拟环境

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
python3.12 -m venv venv  # 使用Python 3.12
```

### 2. 激活虚拟环境

**macOS/Linux**:
```bash
source venv/bin/activate
```

**Windows**:
```bash
venv\Scripts\activate
```

激活后，命令行提示符会显示 `(venv)`。

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行服务

```bash
python3 run_server.py
```

### 5. 退出虚拟环境

```bash
deactivate
```

## 使用conda设置环境（可选）

如果选择使用conda：

### 1. 安装miniconda

```bash
# macOS (使用Homebrew)
brew install miniconda

# 或下载安装包
# https://docs.conda.io/en/latest/miniconda.html
```

### 2. 初始化conda

```bash
conda init zsh  # 如果使用zsh
# 或
conda init bash  # 如果使用bash
```

### 3. 创建conda环境

```bash
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified/api
conda create -n dict-api python=3.11
conda activate dict-api
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 运行服务

```bash
python3 run_server.py
```

### 6. 退出环境

```bash
conda deactivate
```

## 项目推荐配置

### 使用venv（推荐）

在项目根目录创建虚拟环境：

```bash
# 在unified目录创建虚拟环境（便于多个模块共享）
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
python3.12 -m venv venv  # 使用Python 3.12
source venv/bin/activate

# 安装依赖
cd api
pip install -r requirements.txt

# 运行服务
python3 run_server.py
```

### .gitignore配置

如果使用venv，建议在 `.gitignore` 中添加：

```
venv/
.venv/
env/
.env
*.pyc
__pycache__/
```

## 建议

**对于当前项目，推荐使用venv**，因为：
1. ✅ 简单易用，Python内置
2. ✅ 项目依赖简单（FastAPI、asyncpg等）
3. ✅ 不需要管理多个Python版本
4. ✅ 启动快速，占用空间小

**如果将来需要**：
- 管理多个Python版本
- 使用科学计算包（NumPy、Pandas等）
- 更复杂的依赖管理

**则可以考虑使用conda**。

## 快速开始（使用venv）

```bash
# 1. 创建虚拟环境（使用Python 3.12）
cd /Users/fangyu/work/fishenglish/Daemon/dict/src/unified
python3.12 -m venv venv

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
cd api
pip install -r requirements.txt

# 4. 运行服务
python3 run_server.py
```

## 常用命令

### venv

```bash
# 创建环境
python3 -m venv venv

# 激活
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 退出
deactivate

# 查看已安装包
pip list

# 导出依赖
pip freeze > requirements.txt
```

### conda

```bash
# 创建环境
conda create -n env-name python=3.11

# 激活
conda activate env-name

# 退出
conda deactivate

# 查看环境列表
conda env list

# 删除环境
conda env remove -n env-name
```

