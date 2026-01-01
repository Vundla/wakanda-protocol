defmodule Backend.PluginManager do
  use GenServer
  import Ecto.Query
  alias Backend.RepoCockroach
  alias Backend.Schema.{Protocol, Event}

  @timeout 2_000
  @plugin_timeout 1_000

  ## Client API

  def start_link(_args) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def call(plugin_id, payload) when is_atom(plugin_id) do
    GenServer.call(__MODULE__, {:call, plugin_id, payload}, @timeout)
  end

  ## Server callbacks

  @impl true
  def init(_state) do
    plugins = load_plugins_from_db()
    {:ok, %{plugins: plugins}}
  end

  @impl true
  def handle_call({:call, plugin_id, payload}, _from, state) do
    case Map.fetch(state.plugins, plugin_id) do
      {:ok, module} -> 
        {duration, result} = :timer.tc(fn -> dispatch_call(module, payload, state) end)
        duration_ms = div(duration, 1000)
        
        # Log event asynchronously
        Task.start(fn -> 
          protocol_id = lookup_protocol_id(plugin_id)
          if protocol_id do
            Event.log_plugin_call(protocol_id, payload, elem(result, 1), duration_ms)
          end
        end)
        
        result
      :error -> {:reply, {:error, :unknown_plugin}, state}
    end
  end

  defp lookup_protocol_id(plugin_id) do
    try do
      plugin_id_str = Atom.to_string(plugin_id)
      
      Protocol
      |> where([p], p.plugin_id == ^plugin_id_str and p.status == "active")
      |> select([p], p.id)
      |> RepoCockroach.one()
    rescue
      _ -> nil
    end
  end

  defp load_plugins_from_db do
    fallback = Application.get_env(:backend, :plugins, %{})

    # In test env with test plugins configured, use them
    if Mix.env() == :test and map_size(fallback) > 0 do
      fallback
    else
      try do
        Protocol
        |> where([p], p.status == "active")
        |> RepoCockroach.all()
        |> Enum.reduce(%{}, fn protocol, acc ->
          plugin_id = String.to_existing_atom(protocol.plugin_id)
          module = Protocol.module_name(protocol)

          if module do
            Map.put(acc, plugin_id, module)
          else
            acc
          end
        end)
      rescue
        _ -> fallback
      end
    end
  end

  defp dispatch_call(plugin, payload, state) do
    case ensure_plugin(plugin) do
      {:ok, pid} ->
        reply = safe_call(pid, payload)
        {:reply, reply, state}

      {:error, reason} ->
        {:reply, {:error, reason}, state}
    end
  end

  ## Internal helpers

  defp ensure_plugin(plugin) do
    cond do
      not valid_plugin?(plugin) ->
        {:error, :invalid_plugin}

      pid = Process.whereis(plugin) ->
        {:ok, pid}

      true ->
        start_plugin(plugin)
    end
  end

  defp valid_plugin?(plugin) do
    with {:module, _} <- Code.ensure_loaded(plugin),
         true <- function_exported?(plugin, :handle, 1),
         true <- function_exported?(plugin, :start_link, 1),
         true <- function_exported?(plugin, :handle_call, 3) do
      true
    else
      _ -> false
    end
  end

  defp start_plugin(plugin) do
    case DynamicSupervisor.start_child(Backend.PluginSupervisor, {plugin, []}) do
      {:ok, pid} -> {:ok, pid}
      {:error, {:already_started, pid}} -> {:ok, pid}
      {:error, _} -> {:error, :plugin_unavailable}
    end
  end

  defp safe_call(pid, payload) do
    try do
      GenServer.call(pid, payload, @plugin_timeout)
    catch
      :exit, _ -> {:error, :plugin_crashed}
    end
  end
end
