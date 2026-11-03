# The MCP server as a container: Hugging Face Space (Docker), an Oracle Cloud Always Free VM, or any host.
# Secrets come from the environment: HF_TOKEN, MCP_TOKEN, optional GH_DISPATCH_TOKEN, HF_REPO, GH_REPO.
FROM python:3.11-slim
RUN useradd -m -u 1000 app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY mcp_server.py server/mcp_server.py
USER app
ENV PORT=7860
EXPOSE 7860
CMD ["python", "server/mcp_server.py", "--http"]
