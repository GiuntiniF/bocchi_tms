FROM python:3.8.3-alpine


# Install dependencies
COPY requirements.txt .

# RUN apk update
RUN apk update && apk add python3-dev \
    gcc \
    libc-dev \
    libffi-dev
RUN pip install --upgrade pip
RUN pip install --user -r requirements.txt

# Copy source code
COPY . .