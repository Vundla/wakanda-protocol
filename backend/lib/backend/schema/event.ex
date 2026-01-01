defmodule Backend.Schema.Event do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:id, :binary_id, autogenerate: true}
  @foreign_key_type :binary_id

  schema "events" do
    field :user_id, :binary_id
    field :protocol_id, :binary_id
    field :event_type, :string
    field :payload, :map
    field :result, :map
    field :status, :string
    field :duration_ms, :integer
    field :error, :string

    timestamps(type: :utc_datetime_usec, updated_at: false)
  end

  @doc false
  def changeset(event, attrs) do
    event
    |> cast(attrs, [:user_id, :protocol_id, :event_type, :payload, :result, :status, :duration_ms, :error])
    |> validate_required([:event_type, :status])
    |> validate_inclusion(:status, ["success", "failure", "timeout", "unavailable"])
  end

  def log_plugin_call(protocol_id, payload, result, duration_ms) do
    attrs = %{
      protocol_id: protocol_id,
      event_type: "plugin_call",
      payload: sanitize_payload(payload),
      result: sanitize_result(result),
      status: status_from_result(result),
      duration_ms: duration_ms,
      error: error_from_result(result)
    }

    %__MODULE__{}
    |> changeset(attrs)
    |> Backend.RepoCockroach.insert()
  end

  defp sanitize_payload(payload) when is_binary(payload), do: %{data: payload}
  defp sanitize_payload(payload) when is_map(payload), do: payload
  defp sanitize_payload(payload), do: %{value: inspect(payload)}

  defp sanitize_result({:ok, value}), do: %{value: inspect(value)}
  defp sanitize_result({:error, reason}), do: %{error: inspect(reason)}
  defp sanitize_result(other), do: %{raw: inspect(other)}

  defp status_from_result({:ok, _}), do: "success"
  defp status_from_result({:error, :plugin_crashed}), do: "failure"
  defp status_from_result({:error, :plugin_unavailable}), do: "unavailable"
  defp status_from_result({:error, _}), do: "failure"
  defp status_from_result(_), do: "failure"

  defp error_from_result({:error, reason}), do: inspect(reason)
  defp error_from_result(_), do: nil
end
