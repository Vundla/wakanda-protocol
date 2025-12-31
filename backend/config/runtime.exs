import Config

config :backend, Backend.Config,
  port: String.to_integer(System.get_env("PORT") || "5001"),
  cors_origin: System.get_env("CORS_ORIGIN") || "*"
