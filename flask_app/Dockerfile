FROM python:3.11-alpine AS build
WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/python -r requirements.txt

COPY . .

FROM gcr.io/distroless/python3-debian12 AS runtime
WORKDIR /app

COPY --from=build /python/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /python/bin /usr/local/bin

COPY --from=build /build/app.py .

COPY --from=build /build/templates ./templates

COPY --from=build /build/static ./static

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

EXPOSE 4000
CMD ["app.py"]