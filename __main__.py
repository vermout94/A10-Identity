import pulumi
from pulumi_azuread import get_user
from pulumi_azure_native import authorization, resources
import uuid

# Configuration
email = "wi22b116@technikum-wien.at"  # Email of the user for role assignment and queries
resource_group_name = "my-resource-group"  # Replace with your desired resource group name
config = pulumi.Config("azure")
location = "eastus"
subscription_id = config.require("subscriptionId")

# Function to create a resource group
def create_resource_group(resource_group_name, location):
    """
    Create a resource group.
    """
    resource_group = resources.ResourceGroup(
        resource_group_name,
        resource_group_name=resource_group_name,
        location=location,
    )
    pulumi.log.info(f"Created resource group: {resource_group_name}")
    return resource_group

# Function to assign the Reader role to the user
def assign_reader_role(user_object_id, resource_group):
    """
    Assign the 'Reader' role to a user for the specified resource group.
    """
    # Reader role definition ID (common ID for Reader role in Azure)
    reader_role_definition_id = (
        f"/subscriptions/{subscription_id}/providers/Microsoft.Authorization/"
        "roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7"
    )

    # Generate a unique name for the role assignment
    role_assignment_name = str(uuid.uuid4())

    # Create the role assignment
    role_assignment = authorization.RoleAssignment(
        f"readerRoleAssignment-{role_assignment_name}",
        scope=resource_group.id,
        role_assignment_name=role_assignment_name,
        principal_id=user_object_id,
        role_definition_id=reader_role_definition_id,
        principal_type="User",
    )

    pulumi.log.info(f"Assigned 'Reader' role to user: {user_object_id}")
    return role_assignment.id

# Main execution flow
if __name__ == "__main__":
    # Fetch the user object
    user = get_user(user_principal_name=email)

    # Step 1: Create the resource group
    resource_group = create_resource_group(resource_group_name, location)

    # Step 2: Assign the Reader role to the user for the created resource group
    role_assignment_id = assign_reader_role(user.object_id, resource_group)

    # Export results
    pulumi.export("resourceGroupName", resource_group.name)
    pulumi.export("resourceGroupLocation", resource_group.location)
    pulumi.export("assignedRoleId", role_assignment_id)
