defmodule Backend.Application do
  use Application

  @impl true
  def start(_type, _args) do
    Backend.GleamLoader.add_paths()

    port = Backend.Config.port()

    children = 
      if Mix.env() == :test do
        [
          Backend.Repo,
          Backend.RepoReplica,
          Backend.RepoCockroach,
          Backend.PluginSupervisor,
          {Plug.Cowboy, scheme: :http, plug: Backend.Router, options: [port: port]}
        ]
      else
        [
          Backend.Repo,
          Backend.RepoReplica,
          Backend.RepoCockroach,
          Backend.PluginSupervisor,
          Backend.PluginManager,
          {Plug.Cowboy, scheme: :http, plug: Backend.Router, options: [port: port]}
        ]
      end

    opts = [strategy: :one_for_one, name: Backend.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
