FROM python:3.10

ARG REQUIREMENTS_FILE

WORKDIR /app
ENV PYTHONUNBUFFERED 1

RUN set -x && \
	apt-get update && \
	apt -f install	&& \
	apt-get -qy install netcat && \
	apt-get install -y postgresql-client && \
	rm -rf /var/lib/apt/lists/* && \
	wget -O /wait-for https://raw.githubusercontent.com/eficode/wait-for/master/wait-for && \
	chmod +x /wait-for

COPY ./docker/ /
COPY ./requirements/ ./requirements
COPY requirements.txt requirements.txt

ENV PATH="/root/.local/bin:$PATH"
RUN pip install -r requirements.txt
ENV PYTHONPATH "${PYTHONPATH}:/app/bhealthapp"

COPY . ./

