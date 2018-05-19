FROM python:3

# Create app folder
RUN mkdir -p /usr/src/app

# Set PWD to the app folder
WORKDIR /usr/src/app

# Bundle app source
COPY . /usr/src/app

RUN pip install requests emoji python-telegram-bot

CMD [ "python", "./hack_bot.py" ]

