import Config

# Configure Ecto repos
config :backend,
  ecto_repos: [Backend.Repo, Backend.RepoReplica, Backend.RepoCockroach]

# Test database configuration
config :backend, Backend.Repo,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "backend_test",
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: 10

config :backend, Backend.RepoReplica,
  username: "postgres",
  password: "postgres",
  hostname: "localhost",
  database: "backend_replica_test",
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: 10

config :backend, Backend.RepoCockroach,
  username: "root",
  password: "",
  hostname: "localhost",
  database: "backend_cockroach_test",
  pool: Ecto.Adapters.SQL.Sandbox,
  pool_size: 10
