import Config

# Configure Ecto repos
config :backend,
  ecto_repos: [Backend.Repo, Backend.RepoReplica, Backend.RepoCockroach]

config :logger, :console,
  format: "$time $metadata[$level] $message\n",
  metadata: [:request_id]

config :backend, Backend.Config,
  port: String.to_integer(System.get_env("PORT") || "5001"),
  cors_origin: System.get_env("CORS_ORIGIN")
