FROM python:latest

RUN mkdir -p /opt/healthcare-workflow
WORKDIR /opt/healthcare-workflow

RUN mkdir -p /opt/certs
COPY ./keys/* /opt/certs/
COPY ./keys/ca-cert.crt /usr/share/ca-certificates
RUN update-ca-certificates

COPY requirements.txt requirements.txt

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt

COPY ./src/*.py /opt/healthcare-workflow

CMD [ "python3","-u","/opt/healthcare-workflow/Exec.py" , "", ""]