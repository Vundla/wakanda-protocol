defmodule Backend.PluginManagerTest do
  use ExUnit.Case, async: false

  setup do
    Application.put_env(:backend, :plugins, %{
      gleam: Backend.Plugin.Gleam,
      good: Backend.TestPlugins.Good,
      crash: Backend.TestPlugins.Crash,
      invalid: Backend.TestPlugins.Invalid
    })

    unless Process.whereis(Backend.PluginSupervisor) do
      start_supervised!(Backend.PluginSupervisor)
    end

    start_supervised!(Backend.PluginManager)

    on_exit(fn -> Application.delete_env(:backend, :plugins) end)
    :ok
  end

  test "successful plugin call delegates to plugin" do
    assert {:ok, {:echo, "hi"}} = Backend.PluginManager.call(:good, "hi")
  end

  test "invalid plugin is rejected" do
    assert {:error, :invalid_plugin} = Backend.PluginManager.call(:invalid, :payload)
  end

  test "crashed plugin reports failure" do
    assert {:error, :plugin_crashed} = Backend.PluginManager.call(:crash, :boom)
  end

  test "unknown plugin id is reported" do
    assert {:error, :unknown_plugin} = Backend.PluginManager.call(:ghost, :payload)
  end

  test "gleam plugin failure surfaces as error" do
    assert {:error, :gleam_failed} = Backend.PluginManager.call(:gleam, :force_error)
  end

end
