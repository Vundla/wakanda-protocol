defmodule Backend.GleamLoader do
  @moduledoc """
  Adds Gleam build artifacts to the BEAM code path if they exist.
  """

  require Logger

  @gleam_app "backend_gleam"

  @doc """
  Append Gleam ebin directories for dev/prod builds when present.
  """
  def add_paths do
    for env <- ["dev", "prod"] do
      path = build_path(env)

      if File.dir?(path) do
        Code.append_path(path)
        Logger.info("Added Gleam code path: #{path}")
      else
        Logger.debug("Gleam code path missing (build not run yet): #{path}")
      end
    end

    :ok
  end

  defp build_path(env) do
    Path.expand("../../build/#{env}/erlang/#{@gleam_app}/ebin", __DIR__)
  end
end
