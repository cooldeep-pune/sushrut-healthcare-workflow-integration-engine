FROM python:latest

RUN mkdir -p /opt/healthcare-workflow
RUN mkdir -p /opt/scripts

WORKDIR /opt/healthcare-workflow

COPY requirements.txt requirements.txt

RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt

COPY *.py /opt/scripts

RUN echo 'alias cli="python3 /opt/scripts/aie_cli_cmd.py"' >> ~/.bashrc

CMD [ "python3", "/opt/healthcare-workflow/aie_cli_cmd.py" , "", ""]