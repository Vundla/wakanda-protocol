# Wakanda Protocol Backend (Elixir)

Plug + Cowboy API server.

## Prerequisites

- Erlang/OTP and Elixir (installed via apt): `erlang-base erlang-dev erlang-ssl elixir rebar3`
- Hex/Rebar locally: `mix local.hex --force && mix local.rebar --force`
- Gleam 1.14.0 installed to `/usr/local/bin/gleam`

## Setup

```bash
cd backend
mix deps.get
gleam build   # compiles Gleam to BEAM; required for Gleam-backed endpoints
```

## Development

```bash
mix run --no-halt
# or: iex -S mix
```

Server runs on `http://localhost:5001` by default. Configure `PORT` and `CORS_ORIGIN` in your env.

## Testing

```bash
mix test       # Elixir tests
gleam test     # Gleam tests
mix coveralls  # Coverage (text)
mix coveralls.html # Coverage report in html/cover/excoveralls.html
```

## Endpoints

- `GET /health` – health check
- `GET /api` – API info (includes Gleam message when built)
- `GET /gleam` – returns Gleam message, 503 if Gleam not yet built

## Notes

- CORS origin uses `CORS_ORIGIN` (defaults to `*`).
- Logging via `Plug.Logger` + console logger.
