import gleeunit
import gleeunit/should
import backend_gleam

pub fn main() {
  gleeunit.main()
}

pub fn hello_test() {
  backend_gleam.hello("Wakanda")
  |> should.equal("Hello, Wakanda from Gleam")
}

pub fn health_test() {
  backend_gleam.health()
  |> should.equal("ok")
}
