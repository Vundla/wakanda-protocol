defmodule Backend.Repo do
  use Ecto.Repo,
    otp_app: :backend,
    adapter: Ecto.Adapters.Postgres
end

defmodule Backend.RepoReplica do
  use Ecto.Repo,
    otp_app: :backend,
    adapter: Ecto.Adapters.Postgres
end

defmodule Backend.RepoCockroach do
  use Ecto.Repo,
    otp_app: :backend,
    adapter: Ecto.Adapters.Postgres
end
