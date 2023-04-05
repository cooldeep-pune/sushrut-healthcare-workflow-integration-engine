FROM python:3.10.8

RUN mkdir -p /opt/healthcare-workflow
WORKDIR /opt/healthcare-workflow

COPY requirements.txt requirements.txt

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt

COPY ./src/*.py /opt/healthcare-workflow

CMD [ "python3", "/opt/healthcare-workflow/Exec.py" , "", ""]