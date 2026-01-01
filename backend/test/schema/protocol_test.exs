defmodule Backend.Schema.ProtocolTest do
  use ExUnit.Case, async: true
  alias Backend.Schema.Protocol

  describe "changeset/2" do
    test "validates required fields" do
      changeset = Protocol.changeset(%Protocol{}, %{})
      assert changeset.errors[:name]
      assert changeset.errors[:version]
      assert changeset.errors[:plugin_id]
    end

    test "accepts valid protocol" do
      attrs = %{
        name: "test_plugin",
        version: "1.0.0",
        plugin_id: "test",
        status: "active"
      }

      changeset = Protocol.changeset(%Protocol{}, attrs)
      assert changeset.valid?
    end

    test "validates status inclusion" do
      attrs = %{name: "test", version: "1.0", plugin_id: "test", status: "invalid"}
      changeset = Protocol.changeset(%Protocol{}, attrs)
      assert changeset.errors[:status]
    end
  end

  describe "active?/1" do
    test "returns true for active protocol" do
      protocol = %Protocol{status: "active"}
      assert Protocol.active?(protocol)
    end

    test "returns false for inactive protocol" do
      protocol = %Protocol{status: "inactive"}
      refute Protocol.active?(protocol)
    end
  end

  describe "module_name/1" do
    test "returns module atom from config" do
      protocol = %Protocol{config: %{"module" => "Elixir.Backend.Plugin.Gleam"}}
      assert Protocol.module_name(protocol) == Backend.Plugin.Gleam
    end

    test "returns nil for invalid module" do
      protocol = %Protocol{config: %{"module" => "NonExistent.Module"}}
      assert Protocol.module_name(protocol) == nil
    end

    test "returns nil for missing config" do
      protocol = %Protocol{config: %{}}
      assert Protocol.module_name(protocol) == nil
    end
  end
end
