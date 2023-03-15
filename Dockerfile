FROM python:3.10
FROM python:3.10

ARG REQUIREMENTS_FILE

WORKDIR /app
ENV PYTHONUNBUFFERED 1

RUN set -x && \
	apt-get update && \
	apt -f install	&& \
	apt-get -qy install netcat && \
	rm -rf /var/lib/apt/lists/* && \
	wget -O /wait-for https://raw.githubusercontent.com/eficode/wait-for/master/wait-for && \
	chmod +x /wait-for

COPY ./docker/ /
COPY ./requirements/ ./requirements

ENV PATH="/root/.local/bin:$PATH"
RUN pip install -r ./requirements/${REQUIREMENTS_FILE}

COPY . ./

ENV PORT=8000
CMD sh -c 'wait-for $DATABASE_HOST:$DATABASE_PORT -- gunicorn --bind 0.0.0.0:$PORT src.wsgi'
