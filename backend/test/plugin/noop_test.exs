defmodule Backend.Plugin.NoopTest do
  use ExUnit.Case, async: true

  test "echoes payload" do
    assert {:ok, "ping"} = Backend.Plugin.Noop.handle("ping")
  end
end
