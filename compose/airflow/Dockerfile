# airflow/Dockerfile
FROM apache/airflow:2.10.3-python3.12

COPY requirements.txt /requirements.txt

USER root
RUN mkdir -p /tmp/constraints && \
    chown -R airflow: /tmp/constraints

USER airflow
RUN curl -Lo /tmp/constraints/constraints.txt https://raw.githubusercontent.com/apache/airflow/constraints-2.10.3/constraints-3.12.txt && \
    pip install --no-cache-dir -r /requirements.txt --constraint /tmp/constraints/constraints.txt

USER root
RUN rm -rf /tmp/constraints

USER airflow