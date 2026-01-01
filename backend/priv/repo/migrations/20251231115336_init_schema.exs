defmodule Backend.Repo.Migrations.InitSchema do
  use Ecto.Migration

  def change do
    # Users table - core authentication and identity
    create table(:users, primary_key: false) do
      add :id, :uuid, primary_key: true
      add :username, :string, null: false
      add :email, :string, null: false
      add :password_hash, :string, null: false
      add :status, :string, default: "active", null: false
      add :role, :string, default: "user", null: false
      add :metadata, :map, default: %{}

      timestamps(type: :utc_datetime_usec)
    end

    create unique_index(:users, [:username])
    create unique_index(:users, [:email])
    create index(:users, [:status])
    create index(:users, [:role])

    # Sessions table - authentication sessions with fault isolation
    create table(:sessions, primary_key: false) do
      add :id, :uuid, primary_key: true
      add :user_id, references(:users, type: :uuid, on_delete: :delete_all), null: false
      add :token_hash, :string, null: false
      add :expires_at, :utc_datetime_usec, null: false
      add :device_info, :map, default: %{}
      add :ip_address, :string
      add :revoked_at, :utc_datetime_usec

      timestamps(type: :utc_datetime_usec, updated_at: false)
    end

    create unique_index(:sessions, [:token_hash])
    create index(:sessions, [:user_id])
    create index(:sessions, [:expires_at])

    # Protocols table - plugin protocol definitions
    create table(:protocols, primary_key: false) do
      add :id, :uuid, primary_key: true
      add :name, :string, null: false
      add :version, :string, null: false
      add :plugin_id, :string, null: false
      add :config, :map, default: %{}
      add :status, :string, default: "active", null: false
      add :metadata, :map, default: %{}

      timestamps(type: :utc_datetime_usec)
    end

    create unique_index(:protocols, [:name, :version])
    create index(:protocols, [:plugin_id])
    create index(:protocols, [:status])

    # Events table - audit log for plugin execution and system events
    create table(:events, primary_key: false) do
      add :id, :uuid, primary_key: true
      add :user_id, references(:users, type: :uuid, on_delete: :nilify_all)
      add :protocol_id, references(:protocols, type: :uuid, on_delete: :nilify_all)
      add :event_type, :string, null: false
      add :payload, :map, default: %{}
      add :result, :map, default: %{}
      add :status, :string, null: false
      add :duration_ms, :integer
      add :error, :text

      timestamps(type: :utc_datetime_usec, updated_at: false)
    end

    create index(:events, [:user_id])
    create index(:events, [:protocol_id])
    create index(:events, [:event_type])
    create index(:events, [:status])
    create index(:events, [:inserted_at])
  end
end
