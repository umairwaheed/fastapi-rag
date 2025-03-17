# start with a minimal image
FROM debian:bookworm-slim

# install base dependencies
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# create the runtime environment for the app
RUN useradd -ms /bin/bash app
RUN mkdir -p /app && chown app:app /app

# create data directory
RUN mkdir -p /data && chown app:app /data

USER app
WORKDIR /app

# fetch the Oso Dev Server
RUN curl https://oso-local-development-binary.s3.amazonaws.com/latest/oso-local-development-binary-linux-x86_64.tar.gz --output oso-dev-server.tar.gz && tar -xzf oso-dev-server.tar.gz && rm oso-dev-server.tar.gz

RUN chmod +x ./standalone

ENV OSO_DIRECTORY=/data
ENV OSO_PORT=8081

COPY policy.polar /app

ENTRYPOINT ["/app/standalone", "policy.polar"]
