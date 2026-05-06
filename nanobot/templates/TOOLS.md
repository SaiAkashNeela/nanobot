# Tool Usage Notes

Tool signatures are provided automatically via function calling.
This file documents non-obvious constraints and usage patterns.

## exec — Safety Limits

- Commands have a configurable timeout (default 60s)
- Dangerous commands are blocked (rm -rf, format, dd, shutdown, etc.)
- Output is truncated at 10,000 characters
- `restrictToWorkspace` config can limit file access to the workspace

## glob — File Discovery

- Use `glob` to find files by pattern before falling back to shell commands
- Simple patterns like `*.py` match recursively by filename
- Use `entry_type="dirs"` when you need matching directories instead of files
- Use `head_limit` and `offset` to page through large result sets
- Prefer this over `exec` when you only need file paths

## grep — Content Search

- Use `grep` to search file contents inside the workspace
- Default behavior returns only matching file paths (`output_mode="files_with_matches"`)
- Supports optional `glob` filtering plus `context_before` / `context_after`
- Supports `type="py"`, `type="ts"`, `type="md"` and similar shorthand filters
- Use `fixed_strings=true` for literal keywords containing regex characters
- Use `output_mode="files_with_matches"` to get only matching file paths
- Use `output_mode="count"` to size a search before reading full matches
- Use `head_limit` and `offset` to page across results
- Prefer this over `exec` for code and history searches
- Binary or oversized files may be skipped to keep results readable

## cron — Scheduled Reminders

- Please refer to cron skill for usage.

## Web Hosting & Demos

- The bot can host static web content (HTML, JS, CSS) via the `www` directory in its workspace.
- To create a demo or show a web task, write files to `www/<task_id>/index.html`.
- These files are served by the gateway and can be viewed by the user at `/www/<task_id>/`.
- This is the preferred way to show interactive demos, dashboards, or any generated UI.
## Container Admin & Self-Evolution

- You have full "Admin" privileges inside your Docker container.
- You can access and modify any file in the container, including your own source code (`nanobot/`) and the WebUI code (`webui/`).
- Use this power to improve yourself, fix bugs, or add new features to your own dashboard.

## Full-Stack Applications

- You are a senior full-stack engineer. When a user asks for an app (e.g., "Build a todo app"), you should:
    1. **Plan**: Design the architecture (e.g., React frontend + Python/FastAPI backend).
    2. **Backend**: Write the backend code and use `start_service` to run it. Always use `task_id` for isolation.
    3. **Frontend**: Create a beautiful UI in `www/<task_id>/`. Ensure it calls the backend via `/proxy/<task_id>/`.
    4. **Deliver**: Provide the user with the direct URL to their new app: `https://<domain>/www/<task_id>/`.
- The system automatically handles port discovery and proxying. Just focus on building the best app possible.

## Sidecar Databases

- **Postgres (pgvector)**: Available at `postgres:5432`.
    - Credentials: User `nanobot`, Password `nanobot_password`, DB `nanobot`.
    - You can create new databases/schemas for specific tasks using `exec` and `psql`.
    - `pgvector` is installed; use it for vector search / embeddings.
- **Redis**: Available at `redis:6379`.
    - Use this for caching, queues, or real-time state.
- **MongoDB**: Available at `mongodb:27017`.
    - Use this for document-based storage or flexible schemas.
- Always use the provided environment variables `POSTGRES_URL`, `REDIS_URL`, and `MONGO_URL` in the apps you build.
