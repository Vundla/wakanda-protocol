defmodule Backend.Config do
  @moduledoc """
  Simple runtime config sourced from environment variables.
  """

  def port do
    Application.get_env(:backend, __MODULE__)[:port]
  end

  def cors_origin do
    Application.get_env(:backend, __MODULE__)[:cors_origin] || "*"
  end
end
