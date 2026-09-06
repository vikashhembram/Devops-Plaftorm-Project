terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstatedf3f72f4"
    container_name       = "tfstate"
    key                  = "terrafrom.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>4.0"
    }
  }
}

provider "azurerm" {
  features {

  }
}

resource "azurerm_resource_group" "terraform_demo" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    environment = "learning"
    managed_by  = "terraform"
  }
}


resource "azurerm_container_registry" "acr" {
  name                = "devopsplatformacr"
  resource_group_name = "observability-rg"
  sku                 = "Basic"
  location            = "East US"
  admin_enabled       = false
}