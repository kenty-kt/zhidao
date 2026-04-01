FROM python:3.12-alpine

WORKDIR /app
COPY ["AI深度分析金融界面 (11).html", "/app/index.html"]
COPY ["app.py", "/app/app.py"]

EXPOSE 80
CMD ["python3", "/app/app.py"]
