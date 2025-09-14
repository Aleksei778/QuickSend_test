FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    supervisor \
    vim \
    git \
    gcc \
    g++ \
    libpq-dev \
    redis-tools \
    curl \
    procps \
    && apt-get clean -y \
    && apt-get autoclean -y \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/*

RUN mkdir -p /var/run/supervisor /var/log/supervisor

RUN mkdir -p /app
RUN chown -R user:user /app

EXPOSE 5555

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY ./docker/supervisor/supervisor.conf /etc/supervisor/supervisor.conf
COPY ./docker/supervisor/conf.d/ /etc/supervisor/conf.d/

COPY . .

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]