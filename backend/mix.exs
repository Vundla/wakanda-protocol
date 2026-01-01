defmodule Backend.MixProject do
  use Mix.Project

  def project do
    [
      app: :backend,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps(),
      test_coverage: [tool: ExCoveralls],
      preferred_cli_env: [
        coveralls: :test,
        "coveralls.detail": :test,
        "coveralls.post": :test,
        "coveralls.html": :test
      ]
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {Backend.Application, []}
    ]
  end

  defp deps do
    [
      {:plug, "~> 1.15"},
      {:plug_cowboy, "~> 2.7"},
      {:jason, "~> 1.4"},
      {:ecto_sql, "~> 3.11"},
      {:postgrex, "~> 0.17"},
      {:excoveralls, "~> 0.18", only: :test, runtime: false}
    ]
  end
end
