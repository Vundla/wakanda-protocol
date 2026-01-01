defmodule Backend.TestPlugins.Good do
  use GenServer

  def start_link(_args) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  def init(:ok), do: {:ok, nil}

  def handle(payload), do: {:ok, {:echo, payload}}

  def handle_call(payload, _from, state) do
    {:reply, handle(payload), state}
  end
end

defmodule Backend.TestPlugins.Crash do
  use GenServer

  def start_link(_args) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  def init(:ok), do: {:ok, nil}

  def handle(_payload), do: {:error, :boom}

  def handle_call(_payload, _from, _state), do: raise("kaboom")
end

defmodule Backend.TestPlugins.Invalid do
  def start_link(_args) do
    Agent.start_link(fn -> :ok end, name: __MODULE__)
  end
end
