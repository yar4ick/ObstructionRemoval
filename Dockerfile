#Instruction to get Python 3.7.9 (Debian)
FROM python:3.7.9-slim
#Setting the working directory
WORKDIR /core
#Install environment dependencies
RUN apt-get update && apt-get -y install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
#Copy list of python requirements
COPY requirements.txt .
#Install python dependencies
#RUN pip install --upgrade pip
RUN pip install -r requirements.txt
#Copy main code
COPY . .
#Run bot
ENTRYPOINT [ "python", "bot.py" ]