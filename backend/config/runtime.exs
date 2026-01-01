import Config

config :backend, Backend.Config,
  port: String.to_integer(System.get_env("PORT") || "5001"),
  cors_origin: System.get_env("CORS_ORIGIN") || "*"

# Main PostgreSQL database
config :backend, Backend.Repo,
  username: System.get_env("DB_USER") || "national_unity",
  password: System.get_env("DB_PASSWORD") || "northeastMv@10111",
  hostname: System.get_env("DB_HOST") || "localhost",
  database: System.get_env("DB_NAME") || "wakanda_db",
  port: String.to_integer(System.get_env("DB_PORT") || "5432"),
  pool_size: String.to_integer(System.get_env("DB_POOL_SIZE") || "10")

# PostgreSQL replica
config :backend, Backend.RepoReplica,
  username: System.get_env("DB_REPLICA_USER") || "national_unity",
  password: System.get_env("DB_REPLICA_PASSWORD") || "northeastMv@10111",
  hostname: System.get_env("DB_REPLICA_HOST") || "localhost",
  database: System.get_env("DB_REPLICA_NAME") || "wakanda_db",
  port: String.to_integer(System.get_env("DB_REPLICA_PORT") || "5433"),
  pool_size: String.to_integer(System.get_env("DB_REPLICA_POOL_SIZE") || "10")

# CockroachDB
config :backend, Backend.RepoCockroach,
  username: System.get_env("COCKROACH_USER") || "root",
  password: System.get_env("COCKROACH_PASSWORD") || "",
  hostname: System.get_env("COCKROACH_HOST") || "localhost",
  database: System.get_env("COCKROACH_DB") || "wakanda_db",
  port: String.to_integer(System.get_env("COCKROACH_PORT") || "26257"),
  pool_size: String.to_integer(System.get_env("COCKROACH_POOL_SIZE") || "10"),
  migration_lock: false

