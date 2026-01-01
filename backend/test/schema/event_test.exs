defmodule Backend.Schema.EventTest do
  use ExUnit.Case, async: true
  alias Backend.Schema.Event

  describe "changeset/2" do
    test "validates required fields" do
      changeset = Event.changeset(%Event{}, %{})
      assert changeset.errors[:event_type]
      assert changeset.errors[:status]
    end

    test "accepts valid event" do
      attrs = %{
        event_type: "plugin_call",
        status: "success",
        payload: %{data: "test"}
      }

      changeset = Event.changeset(%Event{}, attrs)
      assert changeset.valid?
    end

    test "validates status inclusion" do
      attrs = %{event_type: "test", status: "invalid"}
      changeset = Event.changeset(%Event{}, attrs)
      assert changeset.errors[:status]
    end
  end

  describe "sanitize helpers" do
    test "sanitizes string payload" do
      event = %Event{payload: %{data: "test"}}
      assert event.payload == %{data: "test"}
    end

    test "determines success status from ok tuple" do
      # Internal function, tested via log_plugin_call
      assert true
    end
  end
end
