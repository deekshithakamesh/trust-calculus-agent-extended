FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY . /app

RUN python -m pip install --upgrade pip \
    && python -m pip install -e . \
    && python -m pip install pytest

CMD ["python", "-c", "from trustcalc import PolicyEngine, PolicyEnforcer, TaintTracker; print('TrustCalc deployment smoke check passed')"]
