```
                                 ___
                                /   \__
                               (    @\___
                               /         O
                              /   (_____/
                             /_____/   U
         ____  _      _      ____
        |  _ \(_)_  _(_) ___|___ \
        | | | | \ \/ / |/ _ \ __) |
        | |_| | |>  <| |  __// __/
        |____/|_/_/\_\_|\___|_____|

              command & control
```

## About

Dixie2 is a C2 (command-and-control) platform for managing Linux rootkit implants across target machines. It provides a web dashboard for registering clients, monitoring their health via ICMP beacons, dispatching kernel-level commands, and opening interactive reverse shell sessions — all from the browser.

## Features

- **Client Management** — Register targets by identifier, IP, port, and OS type. Edit or remove them at any time.
- **Command Dispatch** — Send commands to one or many clients simultaneously via raw TCP packets. Per-client sent/failed results are tracked.
- **Interactive Terminal** — Open a live reverse shell to any responsive client through an in-browser xterm.js terminal, bridged over WebSocket with automatic PTY upgrade.
- **Health Monitoring** — Listens for ICMP beacons sent by implants at regular intervals. Responsive/unresponsive status is tracked with timestamps.
- **Dashboard** — Live stats (active/inactive/total clients, total commands), a contact rate chart over time, recent command activity, and an interactive ASCII pup.
- **Command History** — Full log of every command sent, with per-client delivery status and expandable detail modals.
- **JWT Authentication** — Token-based auth with 24-hour expiration, password change support.

## Architecture

```
┌─────────────────┐       WebSocket / REST        ┌──────────────────┐
│                  │◄────────────────────────────► │                  │
│  SvelteKit       │        /api/* + /socket.io    │  Flask Backend   │
│  Frontend        │                               │  + SocketIO      │
│  (Node.js)       │                               │  (Python)        │
└─────────────────┘                                └────────┬─────────┘
                                                            │
                                              Raw TCP ──────┤────── ICMP
                                              (commands)    │      (beacons)
                                                            ▲
                                                   ┌────────────────┐
                                                   │  Jolteon        │
                                                   │  Rootkit        │
                                                   │  (Kernel LKM)   │
                                                   └────────────────┘
```

| Layer | Tech |
|-------|------|
| Frontend | SvelteKit 2, Svelte 5, Tailwind CSS, xterm.js, Socket.IO client |
| Backend | Flask, Flask-SocketIO, APScheduler, PyJWT, SQLite |
| Implant | Linux kernel module (Netfilter hooks), raw TCP/ICMP |

## Quickstart

### Prerequisites

- Python 3.10+
- Node.js 18+
- Root/`CAP_NET_RAW` privileges on the C2 server (raw sockets for pings and command packets)

### Backend

```bash
cd Dixie/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "JWT_SECRET=$(openssl rand -hex 32)" > .env
sudo python3 app.py
```

The API server starts on `http://localhost:5001`. Default credentials: `admin` / `admin123`.

### Frontend

```bash
cd Dixie/frontend
npm install
npm run dev -- --host 0.0.0.0
```

The dev server starts on `http://localhost:5173` and proxies API requests to the backend.

## API

Full OpenAPI 3.0.3 spec is available at [`docs/dixie.yaml`](docs/dixie.yaml).

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/login` | Authenticate, get JWT |
| `GET` | `/api/me` | Current user info |
| `POST` | `/api/change-password` | Update password |
| `GET` | `/api/clients` | List all clients |
| `POST` | `/api/clients` | Register a new client |
| `GET` | `/api/clients/:id` | Get client details |
| `PUT` | `/api/clients/:id` | Update a client |
| `DELETE` | `/api/clients/:id` | Remove a client |
| `POST` | `/api/clients/command` | Send command to clients |
| `GET` | `/api/command-history` | Command log with results |
| `GET` | `/api/stats` | Dashboard statistics |
| `GET` | `/api/contact-rate` | Beacon history for charts |
| `GET` | `/api/settings` | Get settings |
| `PUT` | `/api/settings` | Update settings |

### WebSocket Events (Socket.IO)

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client → Server | Authenticate with `{ token }` |
| `start_terminal` | Client → Server | Open reverse shell to `{ client_id }` |
| `terminal_waiting` | Server → Client | Waiting for implant callback |
| `terminal_ready` | Server → Client | Shell session established |
| `terminal_input` | Client → Server | Send keystrokes `{ data }` |
| `terminal_output` | Server → Client | Shell output `{ data }` |
| `terminal_error` | Server → Client | Error `{ message }` |
| `terminal_closed` | Server → Client | Session ended |

## Project Structure

```
Dixie2/
├── Dixie/
│   ├── backend/
│   │   ├── app.py              # Flask + SocketIO server
│   │   ├── ping.py             # ICMP beacon listener
│   │   ├── send_cmd.py         # Raw TCP command dispatch
│   │   ├── send_backdoor.py    # Reverse shell trigger packets
│   │   ├── requirements.txt
│   │   └── .env                # JWT_SECRET (not committed)
│   └── frontend/
│       ├── src/
│       │   ├── routes/(app)/
│       │   │   ├── dashboard/      # Stats, charts, ASCII pup
│       │   │   ├── management/     # Client CRUD + command send
│       │   │   ├── terminal/       # Interactive reverse shell
│       │   │   ├── history/        # Command log
│       │   │   ├── documentation/  # Usage guide
│       │   │   └── settings/       # Config + password
│       │   └── lib/
│       │       ├── auth.ts         # JWT token management
│       │       ├── api.ts          # API client
│       │       └── components/     # Sidebar, shared UI
│       └── package.json
├── Implants/
│   └── Jolteon/                # Linux kernel rootkit (LKM)
│       ├── rootkit/src/        # Netfilter hooks, command handler
│       └── utility/            # Standalone trigger scripts
└── docs/
    └── dixie.yaml              # OpenAPI 3.0.3 spec
```

## License

This project is for authorized security research and educational purposes only.
