defmodule Backend.Plugin.Gleam do
  use GenServer
  @behaviour Backend.Plugin

  @impl Backend.Plugin
  def start_link(_args) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok), do: {:ok, nil}

  @impl Backend.Plugin
  def handle(payload) do
    mod = :backend_gleam

    with {:module, ^mod} <- :code.ensure_loaded(mod),
         true <- function_exported?(mod, :hello, 1) do
      try do
        if payload == :force_error, do: raise("forced_gleam_error")
        {:ok, apply(mod, :hello, [payload])}
      catch
        _, _ -> {:error, :gleam_failed}
      end
    else
      _ -> {:error, :gleam_unavailable}
    end
  end

  @impl true
  def handle_call(payload, _from, state) do
    {:reply, handle(payload), state}
  end
end
