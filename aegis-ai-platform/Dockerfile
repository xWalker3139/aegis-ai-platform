FROM python:3.12-slim
WORKDIR /app
COPY aegis /app/aegis
RUN mkdir /data && chown 10001:10001 /data
USER 10001:10001
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health/live', timeout=2)"
CMD ["python", "-m", "aegis.server"]
