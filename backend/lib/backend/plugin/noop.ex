defmodule Backend.Plugin.Noop do
  use GenServer
  @behaviour Backend.Plugin

  def start_link(_args) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok), do: {:ok, nil}

  @impl Backend.Plugin
  def handle(payload) do
    {:ok, payload}
  end

  @impl true
  def handle_call(payload, _from, state) do
    {:reply, handle(payload), state}
  end
end
