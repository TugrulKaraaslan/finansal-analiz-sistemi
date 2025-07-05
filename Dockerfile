FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m pip install --no-cache-dir -e .
RUN pip install --no-cache-dir filelock
RUN pip install --no-cache-dir pandas-ta==0.3.14b0 --no-binary :all:
CMD ["python", "-m", "finansal_analiz_sistemi"]
