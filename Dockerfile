FROM python:3.12.3-slim

WORKDIR /api

COPY . /api/

RUN pip3 install -r requirements.txt
# Switch to the non-privileged user to run the application.

# Run the application.
CMD ["python3", "api.py"]
