FROM python:3.12-alpine

WORKDIR /code
COPY ./pyproject.toml /code/pyproject.toml
# Get files required by hatch to create the environment
COPY ./src/chatbot/__about__.py /code/src/chatbot/__about__.py
COPY ./README.md /code/README.md
RUN python -m pip install --upgrade pip && pip install hatch
RUN hatch env create
COPY ./api /code/api

CMD ["hatch", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]