FROM python:3.8-slim as build

RUN apt-get -y update && apt-get -y upgrade

WORKDIR /src
COPY . /src

RUN pip install poetry

RUN poetry export --without-hashes -f requirements.txt -o requirements.txt
RUN cat requirements.txt | grep -v 'sys_platform == "win32"' > modified.txt && mv modified.txt requirements.txt
RUN pip wheel -w ./wheels -r requirements.txt
RUN poetry build -f wheel

FROM python:3.8-slim as live
RUN apt-get -y update && apt-get -y upgrade
WORKDIR /app
COPY docker_entry.sh /app
RUN chmod +x /app/docker_entry.sh
COPY --from=build /src/requirements.txt /src/wheels /src/dist/*.whl /desc/
RUN pip install --find-links=/desc -r /desc/requirements.txt /desc/ecs_tool*-py3-none-any.whl
RUN rm -rf /desc
#USER app
ENTRYPOINT ["/app/docker_entry.sh"]
