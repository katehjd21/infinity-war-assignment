variable "db_username" {}
variable "db_password" {
  sensitive = true
}
variable "host" {}
variable "port" {}
variable "database" {}
variable "ssl_mode" {}

variable "secret_key" {
  sensitive = true
}