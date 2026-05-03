FROM python:3.12-slim

WORKDIR /mysite

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x docker/start.sh

CMD ["bash", "docker/start.sh"]
