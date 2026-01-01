defmodule Backend.Router do
  use Plug.Router
  use Plug.ErrorHandler

  require Logger
  import Plug.Conn

  plug Plug.Logger
  plug :put_default_headers
  plug :match
  plug :dispatch

  get "/health" do
    body = Jason.encode!(%{status: "ok", timestamp: DateTime.utc_now()})
    send_resp(conn, 200, body)
  end

  get "/api" do
    gleam_msg =
      case Backend.PluginManager.call(:gleam, "Wakanda") do
        {:ok, msg} -> msg
        {:error, _} -> nil
      end

    body =
      Jason.encode!(%{
        message: "Welcome to Wakanda Protocol API",
        version: "0.1.0",
        gleam: gleam_msg
      })

    send_resp(conn, 200, body)
  end

  get "/gleam" do
    case Backend.PluginManager.call(:gleam, "Wakanda") do
      {:ok, msg} ->
        body = Jason.encode!(%{message: msg})
        send_resp(conn, 200, body)

      {:error, _reason} ->
        body = Jason.encode!(%{error: "Service unavailable"})
        send_resp(conn, 503, body)
    end
  end

  match _ do
    body = Jason.encode!(%{error: "Not Found"})
    send_resp(conn, 404, body)
  end
  defp put_default_headers(conn, _opts) do
    conn
    |> put_resp_content_type("application/json")
    |> put_cors_headers()
  end

  defp put_cors_headers(conn) do
    origin = Backend.Config.cors_origin()

    conn
    |> put_resp_header("access-control-allow-origin", origin)
    |> put_resp_header("access-control-allow-methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
    |> put_resp_header("access-control-allow-headers", "content-type, authorization")
    |> put_resp_header("access-control-allow-credentials", "true")
  end

  @impl true
  def handle_errors(conn, %{reason: reason, stack: stack}) do
    Logger.error("Unhandled error: #{inspect(reason)}\n#{Exception.format_stacktrace(stack)}")

    body = Jason.encode!(%{error: "Internal Server Error"})
    send_resp(conn, conn.status || 500, body)
  end
end
