defmodule Backend.Plugin do
  @moduledoc """
  Contract for hot-pluggable components.
  """

  @callback handle(term()) :: {:ok, term()} | {:error, term()}
  @callback start_link(term()) :: GenServer.on_start()
end
