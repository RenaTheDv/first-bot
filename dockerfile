FROM python:3.10-slim
ENV TOKEN='your_token_here'
COPY . .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "bot.py" ]