#!/usr/bin/env python3
import json
import os

from mcp.server.fastmcp import Context, FastMCP
import requests

octopus_server_uri = 'https://mattc.octopus.app'
octopus_api_key = os.getenv("OCTOPUS_CLI_API_KEY")
headers = {'X-Octopus-ApiKey': octopus_api_key}

# Create an MCP server
mcp = FastMCP("Octopus Space Reset", json_response=True)

def get_octopus_resource(ctx: Context, uri):
    response = requests.get(uri, headers=headers)
    response.raise_for_status()

    return json.loads(response.content.decode('utf-8'))


def get_by_name(ctx: Context, uri, name):
    resources = get_octopus_resource(ctx, uri)
    return next((x for x in resources if x['Name'] == name), None)

@mcp.tool()
async def reset_space(ctx: Context):
    """
    Reset the Scratchpad space in the Octopus instance
    """

    # Define working variables
    space_name = "Scratchpad"
    space_description = "Test space"
    managers_teams = [
        "teams-managers"]  # Either this or manager_team_members must be populated otherwise you'll receive a 400
    manager_team_members = []  # Either this or managers_teams must be populated otherwise you'll receive a 400

    try:
        space = get_by_name(ctx, '{0}/api/spaces/all'.format(octopus_server_uri), space_name)
        space['TaskQueueStopped'] = True

        # update task queue to stopped
        uri = '{0}/api/spaces/{1}'.format(octopus_server_uri, space['Id'])
        response = requests.put(uri, headers=headers, json=space)
        response.raise_for_status()

        # Delete space
        response = requests.delete(uri, headers=headers)
        response.raise_for_status()
    except Exception as e:
        await ctx.log('warning', str(e))
        pass

    # Define space JSON
    space = {
        'Name': space_name,
        'Description': space_description,
        'SpaceManagersTeams': managers_teams,
        'SpaceManagersTeamMembers': manager_team_members,
        'IsDefault': False,
        'TaskQueueStopped': False
    }

    # Create the space
    uri = '{0}/api/spaces'.format(octopus_server_uri)
    response = requests.post(uri, headers=headers, json=space)
    await ctx.log('info', response.text)
    response.raise_for_status()

    # Get the space ID
    space_id = response.json()['Id']

    # Create library variable set
    library_variable_set = {
        'Name': 'Easy Mode Administration',
        'Description': '',
        'Templates': [],
        'VariableSetId': None,
        'ContentType': 'Variables'
    }

    uri = '{0}/api/{1}/libraryvariablesets'.format(octopus_server_uri, space_id)
    response = requests.post(uri, headers=headers, json=library_variable_set)
    response.raise_for_status()

    library_variable_set_response = response.json()
    variable_set_id = library_variable_set_response['VariableSetId']

    # Add variable to the library variable set
    octopus_cli_api_key = os.environ.get('OCTOPUS_CLI_API_KEY', '')

    variable_set = {
        'Id': variable_set_id,
        'OwnerId': library_variable_set_response['Id'],
        'Version': 0,
        'Variables': [
            {
                'Name': 'LibraryVariableSet.Octopus.ApiKey',
                'Value': octopus_cli_api_key,
                'Type': 'String',
                'IsSensitive': True,
                'Scope': {}
            }
        ],
        'ScopeValues': {
            'Environments': [],
            'Machines': [],
            'Actions': [],
            'Roles': [],
            'Channels': [],
            'TenantTags': []
        }
    }

    uri = '{0}/api/{1}/variables/{2}'.format(octopus_server_uri, space_id, variable_set_id)
    response = requests.put(uri, headers=headers, json=variable_set)
    response.raise_for_status()

    await ctx.log('info', 'Created library variable set: Easy Mode Administration')

    # Create AWS OIDC account
    aws_oidc_account = {
        'AccountType': 'AmazonWebServicesOidcAccount',
        'Name': 'AWS OIDC',
        'Description': '',
        'RoleArn': 'arn:aws:iam::381713788115:role/OIDCAdminAccess',
        'SessionDuration': '3600',
        'EnvironmentIds': [],
        'TenantIds': [],
        'TenantTags': [],
        "DeploymentSubjectKeys": [
            "space"
        ],
        "HealthCheckSubjectKeys": [
            "space"
        ],
        "AccountTestSubjectKeys": [
            "space"
        ],
    }

    uri = '{0}/api/{1}/accounts'.format(octopus_server_uri, space_id)
    response = requests.post(uri, headers=headers, json=aws_oidc_account)
    response.raise_for_status()

    await ctx.log('info', 'Created AWS OIDC account: AWS OIDC')

    # Create Azure OIDC account
    azure_oidc_account = {
        'AccountType': 'AzureOidc',
        'Name': 'Azure OIDC',
        'Description': '',
        'TenantId': '3d13e379-e666-469e-ac38-ec6fd61c1166',
        'ClientId': '08a4a027-6f2a-4793-a0e5-e59a3c79189f',
        'SubscriptionNumber': '3b50dcf4-f74d-442e-93cb-301b13e1e2d5',
        'DeploymentSubjectKeys': ['space'],
        'AudienceUri': '',
        'HealthCheckSubjectKeys': ['space'],
        'AccountTestSubjectKeys': ['space'],
        'EnvironmentIds': [],
        'TenantIds': [],
        'TenantTags': []
    }

    uri = '{0}/api/{1}/accounts'.format(octopus_server_uri, space_id)
    response = requests.post(uri, headers=headers, json=azure_oidc_account)
    response.raise_for_status()

    await ctx.log('info', 'Created Azure OIDC account: Azure OIDC')

    # Create environments
    environments = ['Development', 'Test', 'Production']
    for env_name in environments:
        environment = {
            'Name': env_name,
            'Description': '',
            'AllowDynamicInfrastructure': True,
            'UseGuidedFailure': False,
            'SortOrder': 0
        }

        uri = '{0}/api/{1}/environments'.format(octopus_server_uri, space_id)
        response = requests.post(uri, headers=headers, json=environment)
        response.raise_for_status()
        await ctx.log('info', 'Created environment: {0}'.format(env_name))

    await ctx.log('info', space_name)


if __name__ == "__main__":
    mcp.run()

