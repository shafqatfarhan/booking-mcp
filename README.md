# Booking.com MCP Server

This is an MCP server to interact with [Booking.com](https://www.booking.com/) APIs via MCP tools.

## Requirements

- Python >=3.14
**This project requires Python 3.14 or newer.**

## Getting Started

Follow these steps to set up and run the Booking.com MCP server.

### 1. Install Dependencies

It is recommended to use a [virtual environment](https://docs.python.org/3/tutorial/venv.html).

Install `uv` from https://docs.astral.sh/uv/getting-started/installation/

```bash
uv python install 3.14
uv python pin 3.14
uv pip install -r requirements.txt
source ./venv/bin/activate
uv sync
uv run server.py 
```

### 2. Configure Environment Variables

**Configuration uses a `.env` file (which should not be checked in to version control; see `.gitignore`).**

1. Locate the `.example.env` file in the repository.
2. Copy its contents to a new file named `.env`:
   ```bash
   cp .example.env .env
   ```
3. Open `.env` in a text editor and set the flag values (`RAPIDAPI_KEY`, `RAPIDAPI_HOST`, and optionally `API_TIMEOUT_IN_SECONDS`) to reflect your Booking.com RapidAPI credentials and settings.

**Example:**
```
RAPIDAPI_KEY=your_rapidapi_key_here
RAPIDAPI_HOST=your_rapidapi_host_here
API_TIMEOUT_IN_SECONDS=10
```

### 3. Start the Server (Development)

Run the server:

```bash
uv run server.py

or

fastmcp run server.py --transport http --port 9000 --host "0.0.0.0"
```

The server will start and expose the MCP API endpoints.
### 4. Starting the Production Server

To run the server in a production setting, use the `uvicorn` command below. This ensures optimal performance and reliability:

```bash
uvicorn server:app --port 9000 --host "0.0.0.0" --timeout-graceful-shutdown 10 --limit-concurrency 100 --lifespan "on" --ws "websockets-sansio"
```

This command starts the FastMCP HTTP server on port 9000, configured for concurrency and graceful shutdowns.

### 5. Running the Server in Docker (Containerized Deployment)

You can containerize and run this server using Docker for portable and consistent deployments.

#### **a. Build the Docker Image**

```bash
docker build -t fastmcp-app .
```

#### **b. Run the Docker Container**

Replace `<API_Key>` with your actual RapidAPI key:

```bash
docker run -d \
  --name fastmcp \
  -p 9400:9400 \
  -e RAPIDAPI_KEY="<API_Key>" \
  -e RAPIDAPI_HOST="booking-com.p.rapidapi.com" \
  fastmcp-app
```

- The server will now be accessible on port **9400** of your host machine.

#### **c. Stop the Container**

```bash
docker stop fastmcp
```

#### **d. View Container Logs**

```bash
docker logs -f fastmcp
```

#### **e. Rebuild After Code Changes**

If you've made changes to the code and want to rebuild/restart:

```bash
docker stop fastmcp
docker rm fastmcp
docker build -t fastmcp-app .
docker run -d \
  --name fastmcp \
  -p 9400:9400 \
  -e RAPIDAPI_KEY="<API_Key>" \
  -e RAPIDAPI_HOST="booking-com.p.rapidapi.com" \
  fastmcp-app
```


## Features

- **Search Destinations**: Query Booking.com destinations by city name.
- **Fetch Hotels**: Retrieve hotels for a specified destination and date range.


## License

See [LICENSE](./LICENSE) for license terms.
