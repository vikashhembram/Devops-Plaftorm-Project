output "resource_group_name" {
  description = "Name of the Terraform learning resource group"
  value       = azurerm_resource_group.terraform_demo.name
}

output "acr_login_server" {
  description = "Login server URL of the Azure Container Registry"
  value       = azurerm_container_registry.acr.login_server
}