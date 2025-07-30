from mcp.server import FastMCP
import requests

mcp = FastMCP(name="Swagger API", instructions="This MCP tool extracts API definitions from swagger.json endpoints. It returns the paths and schemas in a structured format. First select the correct api for the use case using the base url list tool, then send that url to the get_swagger_api_defs_from_json tool to extract the API definitions.")


@mcp.tool(name= "base_url_list", description="List of base URLs for Swagger API definitions. The agent should select the correct API for the use case from this list by reading the descriptions of each, before using the get_swagger_api_defs_from_json tool.")
def base_url_list():
    """
    List of base URLs for Swagger API definitions.
    The agent should select the correct API for the use case from this list by reading the descriptions of each,
    before using the get_swagger_api_defs_from_json tool.
    :return: List of dictionaries with base URLs and their descriptions.
    """
    return [
        {
            "swaggerJsonUrl": "https://mscc-svc.api.dev-thor-ue1.hpip-internal.com/svc/dcc-notifications/api-docs/swagger.json",
            "baseUrl": "https://mscc-svc.api.dev-thor-ue1.hpip-internal.com/svc/dcc-notifications",
            "description": "DCC Notifications API - Provides access to DCC notifications."
        },
        {
            "swaggerJsonUrl": "https://dss-svc.api.dev-thor-ue1.hpip-internal.com/svc/device-view/api-docs/swagger.json",
            "baseUrl": "https://dss-svc.api.dev-thor-ue1.hpip-internal.com/svc/device-view",
            "description": "Device View API - Provides access to device view functionalities and device data."
        },
        {
            "swaggerJsonUrl": "https://dss-svc.api.dev-thor-ue1.hpip-internal.com/svc/supply-order/api-docs/swagger.json",
            "baseUrl": "https://hpcorp-ob-test.default.api.hp.com/device-view-service-dev/svc/supply-order",
            "description": "Supply Order API - Provides access to supply order functionalities."
        }
    ]


@mcp.tool(
    name="get_swagger_api_defs_from_json",
    description="The agent should first get the Paladdin token, then extract API definitions from swagger.json endpoint."
)
async def get_swagger_api_defs_from_json(swagger_json_url, base_url):
    """
    Fetch swagger.json of a given API using HTTP GET request.
    This function retrieves the API definitions from the provided swagger.json URL and returns the paths and schemas
    """
    try:
        print(f"Fetching Swagger JSON from: {swagger_json_url}")
        
        
        response = requests.get(
            swagger_json_url, 
            verify=False,
        )

        if response.status_code != 200:
            return {"error": f"Failed to load swagger.json. Status code: {response.status_code}"}

        try:
            swagger_data = response.json()
        except Exception as e:
            return {
                "error": f"Failed to parse JSON: {str(e)}",
                "content_preview": response.text[:500]
            }

        paths = swagger_data.get("paths", {})
        schemas = swagger_data.get("components", {}).get("schemas", {})
        if not schemas:
            schemas = swagger_data.get("definitions", {})

        return {
            "paths": paths,
            "schemas": schemas,
            "baseUrl": base_url
        }

    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


if __name__ == "__main__":
    mcp.run()
    print("Swagger API MCP is running...")