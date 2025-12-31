defmodule Backend.Application do
  use Application

  @impl true
  def start(_type, _args) do
    Backend.GleamLoader.add_paths()

    port = Backend.Config.port()

    children = [
      {Plug.Cowboy, scheme: :http, plug: Backend.Router, options: [port: port]}
    ]

    opts = [strategy: :one_for_one, name: Backend.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
