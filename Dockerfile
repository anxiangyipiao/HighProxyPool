# 使用官方 Python 基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目的依赖文件
COPY requirements.txt /app/requirements.txt


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    && apt-get clean


# 安装依赖
RUN pip install --no-cache-dir -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制项目代码到容器中
COPY . /app

# 暴露应用运行的端口
EXPOSE 8000

# 启动 FastAPI 应用
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]