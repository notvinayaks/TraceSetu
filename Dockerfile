# Deployment recipe. Building/running this image requires independent validation.
FROM node:24-bookworm-slim AS ui
WORKDIR /app/frontend
RUN npm install --global pnpm@11.19.0
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile
COPY frontend/ ./
RUN pnpm build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app/backend ATLAS_DATA_DIR=/var/lib/atlas ATLAS_LOCAL_BOOTSTRAP=false
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock && useradd --create-home --uid 10001 atlas && mkdir -p /var/lib/atlas && chown atlas:atlas /var/lib/atlas
COPY backend ./backend
COPY scripts/verify_evidence.py ./scripts/verify_evidence.py
COPY scripts/manage.py scripts/validate_live.py ./scripts/
COPY --from=ui /app/frontend/dist ./frontend/dist
COPY frontend/public/favicon.svg ./frontend/public/favicon.svg
USER atlas
EXPOSE 8787
CMD ["python", "-m", "uvicorn", "vasp_app.main:app", "--app-dir", "backend", "--host", "0.0.0.0", "--port", "8787"]
