# Replace BASE_IMAGE with the observed immutable arm64 digest before building.
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
RUN npm install --global npm@10.9.3 @openai/codex@0.167.0-alpha.3.2 typescript@5.9.3 --ignore-scripts --no-audit --no-fund
RUN npm install --prefix /opt/s2-tools typescript@5.9.3 @types/node@22.20.5 --ignore-scripts --no-audit --no-fund
ENV NODE_PATH=/usr/local/lib/node_modules
USER 1000:1000
WORKDIR /source
