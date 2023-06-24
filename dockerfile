FROM python

COPY . /

RUN pip3 install boto3
RUN pip3 install pyjwt -t .
RUN pip3 install fastapi
RUN pip3 install uvicorn
RUN pip3 install pydantic

# Download CURL for Health Check
RUN apt update -y
RUN apt upgrade -y
RUN apt install -y curl 

ENV tableName=Booking
EXPOSE 80
ENTRYPOINT [ "python", "Booking-Command.py"]


