alias Backend.RepoCockroach
alias Backend.Schema.Protocol

# Insert Gleam plugin protocol definition
{:ok, _protocol} = RepoCockroach.insert(%Protocol{
  name: "gleam_plugin",
  version: "0.1.0",
  plugin_id: "gleam",
  config: %{
    "module" => "Elixir.Backend.Plugin.Gleam",
    "description" => "Gleam language integration plugin",
    "capabilities" => ["code_execution", "hot_reload"]
  },
  status: "active",
  metadata: %{
    "language" => "gleam",
    "runtime" => "beam"
  }
})

# Insert Noop plugin protocol definition
{:ok, _noop} = RepoCockroach.insert(%Protocol{
  name: "noop_plugin",
  version: "0.1.0",
  plugin_id: "noop",
  config: %{
    "module" => "Elixir.Backend.Plugin.Noop",
    "description" => "No-op plugin echoes payload",
    "capabilities" => ["echo"]
  },
  status: "active",
  metadata: %{
    "language" => "elixir",
    "runtime" => "beam"
  }
})

IO.puts("✅ Seeded Gleam plugin protocol")
IO.puts("✅ Seeded Noop plugin protocol")
