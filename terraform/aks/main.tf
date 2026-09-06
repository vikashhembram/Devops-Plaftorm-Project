terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstatedf3f72f4"
    container_name       = "tfstate"
    key                  = "aks.tfstate"
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 4.0"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "observability"
  location            = "East US"
  resource_group_name = "observability-rg"
  dns_prefix          = "observabil-observability-rg-f811c5"

  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  lifecycle {
    ignore_changes = [
      linux_profile
    ]
  }

  identity {
    type = "SystemAssigned"
  }

  default_node_pool {
    name                 = "nodepool1"
    vm_size              = "standard_d2s_v7"
    node_count           = 2
    auto_scaling_enabled = true
    min_count            = 2
    max_count            = 3

    upgrade_settings {
      max_surge = "10%"
    }
  }

  network_profile {
    network_plugin      = "azure"
    network_plugin_mode = "overlay"
    outbound_type       = "loadBalancer"
    service_cidr        = "10.0.0.0/16"
  }

  role_based_access_control_enabled = true
}