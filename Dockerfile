# 使用 Python 3.10 作为基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 运行 bot.py
CMD ["python", "bot.py"]
