defmodule Backend.RouterTest do
  use ExUnit.Case, async: false
  import Plug.Test
  import Plug.Conn
  alias Backend.Router

  @opts Router.init([])

  setup_all do
    # Ensure Gleam beams are built and on the code path for Gleam-backed endpoints
    System.cmd("gleam", ["build"], cd: Path.expand("..", __DIR__))
    Backend.GleamLoader.add_paths()

    unless Process.whereis(Backend.PluginSupervisor) do
      start_supervised!(Backend.PluginSupervisor)
    end

    unless Process.whereis(Backend.PluginManager) do
      start_supervised!(Backend.PluginManager)
    end
    :ok
  end

  test "/health returns ok" do
    conn = conn(:get, "/health") |> Router.call(@opts)
    assert conn.status == 200
    assert %{"status" => "ok"} = Jason.decode!(conn.resp_body)
  end

  test "/api returns message" do
    conn = conn(:get, "/api") |> Router.call(@opts)
    assert conn.status == 200
    body = Jason.decode!(conn.resp_body)
    assert body["message"] =~ "Wakanda Protocol"
  end

  test "unknown route returns 404" do
    conn = conn(:get, "/nope") |> Router.call(@opts)
    assert conn.status == 404
  end

  test "/health sets JSON and CORS headers" do
    conn = conn(:get, "/health") |> Router.call(@opts)

    assert get_resp_header(conn, "content-type") |> hd() =~ "application/json"
    assert get_resp_header(conn, "access-control-allow-origin") == [Backend.Config.cors_origin()]
    assert get_resp_header(conn, "access-control-allow-methods") == ["GET,POST,PUT,PATCH,DELETE,OPTIONS"]
  end

  test "/gleam returns message when module is present" do
    conn = conn(:get, "/gleam") |> Router.call(@opts)

    assert conn.status == 200
    body = Jason.decode!(conn.resp_body)
    assert is_binary(body["message"])
  end

  test "/gleam returns 503 when Gleam module is missing" do
    gleam_paths =
      :code.get_path()
      |> Enum.filter(fn path ->
        path_str = List.to_string(path)
        String.contains?(path_str, "backend_gleam")
      end)

    Enum.each(gleam_paths, &:code.del_path/1)
    :code.purge(:backend_gleam)
    :code.delete(:backend_gleam)

    conn = conn(:get, "/gleam") |> Router.call(@opts)

    assert conn.status == 503
    body = Jason.decode!(conn.resp_body)
    assert body["error"] == "Service unavailable"

    # Restore Gleam module for subsequent tests
    Enum.each(gleam_paths, &:code.add_patha/1)
    Backend.GleamLoader.add_paths()
  end

  test "handle_errors returns 500 with JSON body" do
    conn = conn(:get, "/err")
    conn = Router.handle_errors(conn, %{reason: RuntimeError.exception("boom"), stack: []})

    assert conn.status == 500
    assert %{"error" => "Internal Server Error"} = Jason.decode!(conn.resp_body)
  end
end
