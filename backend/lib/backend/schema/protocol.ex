defmodule Backend.Schema.Protocol do
  use Ecto.Schema
  import Ecto.Changeset

  @primary_key {:id, :binary_id, autogenerate: true}
  @foreign_key_type :binary_id

  schema "protocols" do
    field :name, :string
    field :version, :string
    field :plugin_id, :string
    field :config, :map
    field :status, :string, default: "active"
    field :metadata, :map

    timestamps(type: :utc_datetime_usec)
  end

  @doc false
  def changeset(protocol, attrs) do
    protocol
    |> cast(attrs, [:name, :version, :plugin_id, :config, :status, :metadata])
    |> validate_required([:name, :version, :plugin_id])
    |> validate_inclusion(:status, ["active", "inactive", "deprecated"])
    |> unique_constraint([:name, :version])
  end

  def active?(protocol), do: protocol.status == "active"

  def module_name(%{config: %{"module" => module}}) when is_binary(module) do
    try do
      String.to_existing_atom(module)
    rescue
      ArgumentError ->
        try do
          String.to_atom(module)
        rescue
          ArgumentError -> nil
        end
    end
  end

  def module_name(_), do: nil
end
