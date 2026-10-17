// Savia IoT - infraestructura Azure equivalente a la practica 1.
// Despliega recursos de pago. Revisar costos y suscripcion antes de ejecutar.
targetScope = 'resourceGroup'

@description('Region de los recursos. North Central US valido en Azure for Students el 17-10-2026; comprobar disponibilidad de nuevo antes de desplegar.')
param location string = 'northcentralus'

@description('IP publica administradora en formato X.X.X.X/32; SSH solo desde esta IP.')
param adminIpCidr string

@description('Clave publica SSH existente; nunca pasar la clave privada.')
param sshPublicKey string

@secure()
@minLength(12)
@description('Contrasena privada del administrador PostgreSQL.')
param dbPassword string

@description('Tamano de VM validado en North Central US el 17-10-2026; confirmar precio y disponibilidad antes de desplegar.')
param vmSize string = 'Standard_B2als_v2'

@description('SKU PostgreSQL Flexible Server; confirmar precio y disponibilidad.')
param dbSku string = 'Standard_B1ms'

@description('Usuario administrador de la VM Ubuntu.')
param adminUser string = 'azureuser'
var dbServerName = 'savia-pg-${uniqueString(resourceGroup().id)}'
var publicSubnetCidr = '10.42.1.0/24'

resource webNsg 'Microsoft.Network/networkSecurityGroups@2023-09-01' = {
  name: 'savia-web-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'AllowHTTP'
        properties: {
          priority: 100
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: 'Internet'
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '80'
        }
      }
      {
        name: 'AllowSSHFromAdmin'
        properties: {
          priority: 110
          protocol: 'Tcp'
          access: 'Allow'
          direction: 'Inbound'
          sourceAddressPrefix: adminIpCidr
          sourcePortRange: '*'
          destinationAddressPrefix: '*'
          destinationPortRange: '22'
        }
      }
    ]
  }
}

resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: 'savia-vnet'
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [ '10.42.0.0/16' ]
    }
  }
}

resource publicSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' = {
  parent: vnet
  name: 'web-publica'
  properties: {
    addressPrefix: publicSubnetCidr
    networkSecurityGroup: {
      id: webNsg.id
    }
  }
}

resource dbSubnet 'Microsoft.Network/virtualNetworks/subnets@2023-09-01' = {
  parent: vnet
  name: 'db-privada'
  properties: {
    addressPrefix: '10.42.11.0/24'
    delegations: [
      {
        name: 'postgres-delegation'
        properties: {
          serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
        }
      }
    ]
  }
}

resource publicIp 'Microsoft.Network/publicIPAddresses@2024-03-01' = {
  name: 'savia-web-ip'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {
    publicIPAllocationMethod: 'Static'
    publicIPAddressVersion: 'IPv4'
  }
}

resource nic 'Microsoft.Network/networkInterfaces@2023-09-01' = {
  name: 'savia-web-nic'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          privateIPAllocationMethod: 'Dynamic'
          subnet: { id: publicSubnet.id }
          publicIPAddress: { id: publicIp.id }
        }
      }
    ]
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2024-07-01' = {
  name: 'savia-web'
  location: location
  properties: {
    hardwareProfile: { vmSize: vmSize }
    storageProfile: {
      imageReference: {
        publisher: 'Canonical'
        offer: '0001-com-ubuntu-server-jammy'
        sku: '22_04-lts-gen2'
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
        managedDisk: { storageAccountType: 'Standard_LRS' }
        diskSizeGB: 30
      }
    }
    osProfile: {
      computerName: 'savia-web'
      adminUsername: adminUser
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUser}/.ssh/authorized_keys'
              keyData: sshPublicKey
            }
          ]
        }
      }
    }
    networkProfile: {
      networkInterfaces: [ { id: nic.id } ]
    }
  }
}

resource privateDns 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'savia.private.postgres.database.azure.com'
  location: 'global'
}

resource dnsLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDns
  name: 'savia-vnet-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: { id: vnet.id }
  }
}

resource postgres 'Microsoft.DBforPostgreSQL/flexibleServers@2024-08-01' = {
  name: dbServerName
  location: location
  sku: {
    name: dbSku
    tier: 'Burstable'
  }
  properties: {
    version: '16'
    administratorLogin: 'saviaadmin'
    administratorLoginPassword: dbPassword
    network: {
      delegatedSubnetResourceId: dbSubnet.id
      privateDnsZoneArmResourceId: privateDns.id
      publicNetworkAccess: 'Disabled'
    }
    highAvailability: { mode: 'Disabled' }
    storage: { storageSizeGB: 32 }
    backup: {
      backupRetentionDays: 7
      geoRedundantBackup: 'Disabled'
    }
  }
  dependsOn: [ dnsLink ]
}

resource database 'Microsoft.DBforPostgreSQL/flexibleServers/databases@2024-08-01' = {
  parent: postgres
  name: 'saviaiot'
  properties: {
    charset: 'UTF8'
  }
}

output webPublicIp string = publicIp.properties.ipAddress
output webHealthUrl string = 'http://${publicIp.properties.ipAddress}/health'
output postgresHost string = '${postgres.name}.postgres.database.azure.com'
output sshUser string = adminUser
output databaseName string = database.name
