#!/usr/bin/env python3
"""
MCP Server for Cloudeka CLI (cldkctl) functionality.
"""

import asyncio
import base64
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from importlib import metadata

import requests
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    Tool,
    TextContent,
    Content,
)


class SimpleNotificationOptions:
    """Simple notification options class for MCP server capabilities."""

    def __init__(self, prompts_changed=False, resources_changed=False, tools_changed=False):
        self.prompts_changed = prompts_changed
        self.resources_changed = resources_changed
        self.tools_changed = tools_changed


# Initialize the server
server = Server("cldkctl")

# Configuration
PRODUCTION_URL = "https://ai.cloudeka.id"
STAGING_URL = "https://staging.ai.cloudeka.id"
CACHE_FILE = os.path.expanduser("~/.cldkctl/mcp_cache.json")
CACHE_DIR = os.path.expanduser("~/.cldkctl")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

# Global state for authentication and environment
auth_cache = {
    "jwt_token": None,
    "login_payload": None,
    "expires_at": None,
    "user_info": None,
    "environment": "production",
    "base_url": PRODUCTION_URL,
}

# Environment configuration
current_base_url = PRODUCTION_URL  # Default to production
environment_name = "production"


def load_cache():
    """Load cached authentication data."""
    global auth_cache, current_base_url, environment_name
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                cached_data = json.load(f)
                # Check if token is still valid
                if cached_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(cached_data["expires_at"])
                    if datetime.now() < expires_at:
                        auth_cache.update(cached_data)
                        current_base_url = auth_cache["base_url"]
                        environment_name = auth_cache["environment"]
                        print(f"Loaded cached auth data, expires at {expires_at}", file=sys.stderr)
                        return True
                    else:
                        print("Cached token expired", file=sys.stderr)
                return False
    except Exception as e:
        print(f"Error loading cache: {e}", file=sys.stderr)
    return False


def save_cache():
    """Save authentication data to cache."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(auth_cache, f, default=str)
    except Exception as e:
        print(f"Error saving cache: {e}", file=sys.stderr)


def authenticate_with_token(token: str, force_staging: bool = False) -> bool:
    """Authenticate using a cldkctl token and get JWT."""
    global auth_cache, current_base_url, environment_name

    # Determine which URL to use
    if force_staging:
        base_url = STAGING_URL
        env_name = "staging"
    else:
        base_url = PRODUCTION_URL
        env_name = "production"

    print(f"Authenticating with {env_name} environment: {base_url}", file=sys.stderr)
    url = f"{base_url}/core/cldkctl/auth"
    payload = {"token": token}

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        print(f"Auth response status: {response.status_code}", file=sys.stderr)

        if response.status_code == 200:
            data = response.json()
            jwt_token = data.get("data", {}).get("token")
            if jwt_token:
                # Update global state
                current_base_url = base_url
                environment_name = env_name
                # Cache the authentication data
                auth_cache["jwt_token"] = jwt_token
                auth_cache["login_payload"] = base64.b64encode(json.dumps(payload).encode()).decode()
                auth_cache["expires_at"] = (datetime.now() + timedelta(hours=24)).isoformat()
                auth_cache["user_info"] = data.get("data", {})
                auth_cache["environment"] = env_name
                auth_cache["base_url"] = base_url
                save_cache()
                print(f"Authentication successful with {env_name}", file=sys.stderr)
                return True
            else:
                print("No JWT token in response", file=sys.stderr)
                return False
        elif response.status_code == 400 and "pq: relation \"cldkctl_tokens\" does not exist" in response.text:
            print("Production backend has database issue, trying staging...", file=sys.stderr)
            if not force_staging:
                return authenticate_with_token(token, force_staging=True)
            else:
                print("Staging also failed with the same issue.", file=sys.stderr)
                return False
        else:
            print(f"Authentication failed: {response.status_code} - {response.text}", file=sys.stderr)
            return False
    except requests.RequestException as e:
        print(f"Authentication request error: {e}", file=sys.stderr)
        if not force_staging:
            print("Trying staging as fallback...", file=sys.stderr)
            return authenticate_with_token(token, force_staging=True)
        return False


def get_auth_headers() -> Dict[str, str]:
    """Get headers with authentication token."""
    if not auth_cache.get("jwt_token"):
        raise Exception("Not authenticated. Please authenticate first.")

    # Check for token expiration
    expires_at_str = auth_cache.get("expires_at")
    if expires_at_str:
        if datetime.now() >= datetime.fromisoformat(expires_at_str):
            print("Token expired, attempting re-authentication", file=sys.stderr)
            if auth_cache.get("login_payload"):
                login_data = json.loads(base64.b64decode(auth_cache["login_payload"]).decode())
                if not authenticate_with_token(login_data["token"], force_staging=(environment_name == "staging")):
                    raise Exception("Re-authentication failed")
            else:
                raise Exception("Token expired and no login payload to re-authenticate.")

    return {
        "Authorization": f"Bearer {auth_cache['jwt_token']}",
        "Content-Type": "application/json",
    }


def make_authenticated_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    """Make an authenticated request to the API."""
    url = f"{current_base_url}{endpoint}"
    try:
        headers = get_auth_headers()
        response = requests.request(method, url, headers=headers, json=data, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Authenticated request failed: {e}", file=sys.stderr)
        # In case of an error, return a structured error message
        return {"error": True, "message": str(e), "status_code": getattr(e.response, "status_code", None)}


# Load cached auth on startup
load_cache()


def get_tool_definitions() -> list[Tool]:
    """Return a list of all tool definitions for the server."""
    return [
        # --- Authentication and Environment ---
        Tool(
            name="auth",
            description="Authenticate with a cldkctl token to get JWT access.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "Your cldkctl token (starts with 'cldkctl_')."},
                    "force_staging": {"type": "boolean", "description": "Force using the staging environment."}
                },
                "required": ["token"]
            }
        ),
        Tool(
            name="switch_environment",
            description="Switch between production and staging environments. This will clear current authentication.",
            inputSchema={
                "type": "object",
                "properties": {
                    "environment": {"type": "string", "enum": ["production", "staging"]}
                },
                "required": ["environment"]
            }
        ),
        Tool(
            name="status",
            description="Show current authentication and environment status.",
            inputSchema={"type": "object", "properties": {}}
        ),

        # --- Project Management ---
        Tool(
            name="project_list",
            description="List all projects for the current organization.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="project_detail",
            description="Get details for a specific project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."}
                },
                "required": ["project_id"]
            }
        ),

        # --- Organization Management ---
        Tool(
            name="org_detail",
            description="Get details for the current organization.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="org_members",
            description="List all members of the current organization.",
            inputSchema={"type": "object", "properties": {}}
        ),

        # --- Balance & Billing ---
        Tool(
            name="balance_detail",
            description="Get balance details for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="billing_daily_cost",
            description="Get the daily cost for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="billing_monthly_cost",
            description="Get the total billed amount for the current month for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="billing_history",
            description="Get billing history for the organization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "month": {"type": "string", "description": "Month in YYYY-MM format (e.g., '2023-10')."},
                    "page": {"type": "integer", "description": "Page number for pagination."},
                    "limit": {"type": "integer", "description": "Items per page."}
                },
                "required": ["project_id", "month", "page", "limit"]
            }
        ),

        # --- Kubernetes (k8s) Management ---
        Tool(
            name="k8s_pods",
            description="List pods in a specific namespace of a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "namespace": {"type": "string", "description": "The Kubernetes namespace.", "default": "default"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="k8s_deployments",
            description="List deployments in a specific namespace of a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "namespace": {"type": "string", "description": "The Kubernetes namespace.", "default": "default"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="k8s_services",
            description="List services in a specific namespace of a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "namespace": {"type": "string", "description": "The Kubernetes namespace.", "default": "default"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="k8s_configmaps",
            description="List configmaps in a specific namespace of a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "namespace": {"type": "string", "description": "The Kubernetes namespace.", "default": "default"}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="k8s_secrets",
            description="List secrets in a specific namespace of a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "namespace": {"type": "string", "description": "The Kubernetes namespace.", "default": "default"}
                },
                "required": ["project_id"]
            }
        ),

        # --- VM Management ---
        Tool(
            name="vm_list",
            description="List all virtual machines for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="vm_detail",
            description="Get details for a specific virtual machine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_id": {"type": "string", "description": "The ID of the virtual machine."}
                },
                "required": ["vm_id"]
            }
        ),
        Tool(
            name="vm_create",
            description="Create a new virtual machine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "name": {"type": "string", "description": "Name of the virtual machine."},
                    "flavor_id": {"type": "string", "description": "Flavor ID for the VM resources."},
                    "image_os_id": {"type": "string", "description": "Image OS ID for the VM."},
                    "root_disk_size": {"type": "integer", "description": "Size of the root disk in GB."},
                    "user_data": {"type": "string", "description": "Cloud-init user data script."},
                },
                "required": ["project_id", "name", "flavor_id", "image_os_id", "root_disk_size", "user_data"]
            }
        ),
        Tool(
            name="vm_delete",
            description="Delete a virtual machine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_id": {"type": "string", "description": "The ID of the virtual machine to delete."}
                },
                "required": ["vm_id"]
            }
        ),
        Tool(
            name="vm_reboot",
            description="Reboot a virtual machine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_id": {"type": "string", "description": "The ID of the virtual machine to reboot."}
                },
                "required": ["vm_id"]
            }
        ),
        Tool(
            name="vm_turn_on",
            description="Turn on a virtual machine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_id": {"type": "string", "description": "The ID of the virtual machine to turn on."}
                },
                "required": ["vm_id"]
            }
        ),
        Tool(
            name="vm_turn_off",
            description="Turn off a virtual machine.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_id": {"type": "string", "description": "The ID of the virtual machine to turn off."}
                },
                "required": ["vm_id"]
            }
        ),

        # --- Container Registry ---
        Tool(
            name="registry_list",
            description="List all container registries for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="registry_repositories",
            description="List repositories in a specific container registry.",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {"type": "string", "description": "The ID of the container registry."}
                },
                "required": ["registry_id"]
            }
        ),

        # --- Deka Notebooks ---
        Tool(
            name="notebook_list",
            description="List all Deka Notebooks for a project.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."}
                },
                "required": ["project_id"]
            }
        ),
        Tool(
            name="notebook_create",
            description="Create a new Deka Notebook.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "The ID of the project."},
                    "name": {"type": "string", "description": "Name of the notebook."},
                    "image": {"type": "string", "description": "Container image for the notebook."},
                    "flavor_id": {"type": "string", "description": "Flavor ID for the notebook resources."}
                },
                "required": ["project_id", "name", "image", "flavor_id"]
            }
        ),

        # --- Voucher Management ---
        Tool(
            name="voucher_list",
            description="List all claimed vouchers.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="voucher_apply",
            description="Apply a voucher code.",
            inputSchema={
                "type": "object",
                "properties": {
                    "voucher_code": {"type": "string", "description": "The voucher code to apply."}
                },
                "required": ["voucher_code"]
            }
        ),

        # --- API Token Management ---
        Tool(
            name="token_list",
            description="List all API tokens for the user.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="token_create",
            description="Create a new API token.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "A name for the token."},
                    "expired_at": {"type": "string", "description": "Expiration date in 'YYYY-MM-DD' format."}
                },
                "required": ["name", "expired_at"]
            }
        ),
        Tool(
            name="token_delete",
            description="Delete an API token.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_id": {"type": "string", "description": "The ID of the token to delete."}
                },
                "required": ["token_id"]
            }
        ),

        # --- Utility Tools ---
        Tool(
            name="audit_logs",
            description="Get audit logs for user activity.",
            inputSchema={"type": "object", "properties": {}}
        ),
    ]


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Provide the list of tools to the MCP client."""
    return get_tool_definitions()


def format_response(data: Any) -> str:
    """Formats API response data for display."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict) and data.get("error"):
        return f"❌ API Error: {data.get('message', 'Unknown error')}"
    return f"```json\n{json.dumps(data, indent=2)}\n```"


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle incoming tool calls from the MCP client."""
    global auth_cache, current_base_url, environment_name
    
    print(f"Received tool call: {name} with arguments: {arguments}", file=sys.stderr)
    
    result_data = None
    is_error = False
    try:
        # --- Authentication and Environment ---
        if name == "auth":
            token = arguments.get("token")
            force_staging = arguments.get("force_staging", False)
            if authenticate_with_token(token, force_staging):
                user_info = auth_cache.get('user_info', {})
                user_data = user_info.get('data', {})
                org_data = user_data.get('organization', {})
                
                result_data = {
                    "status": "✅ Authentication successful",
                    "user": user_data.get('name', 'Unknown'),
                    "role": user_data.get('role', 'Unknown'),
                    "organization": org_data.get('name', 'None'),
                    "environment": auth_cache['environment'],
                    "base_url": auth_cache['base_url']
                }
            else:
                result_data = {"error": True, "message": "❌ Authentication failed. Check logs for details."}
                is_error = True
        
        elif name == "switch_environment":
            env = arguments.get("environment")
            if env == "staging":
                current_base_url = STAGING_URL
                environment_name = "staging"
            else: # Default to production
                current_base_url = PRODUCTION_URL
                environment_name = "production"
            
            # Clear old auth data
            auth_cache = {
                "jwt_token": None, "login_payload": None, "expires_at": None,
                "user_info": None, "environment": environment_name, "base_url": current_base_url
            }
            save_cache() # Persist the new environment setting
            result_data = {
                "status": "Switched environment",
                "message": f"Switched to {environment_name} environment. Please re-authenticate using the 'auth' tool."
            }
            
        elif name == "status":
            if auth_cache.get("jwt_token"):
                user_info = auth_cache.get('user_info', {}).get('data', {})
                result_data = {
                    "status": "Authenticated",
                    "user": user_info.get('name', 'Unknown'),
                    "role": user_info.get('role', 'Unknown'),
                    "organization": user_info.get('organization', {}).get('name', 'None'),
                    "environment": auth_cache.get("environment"),
                    "base_url": auth_cache.get("base_url"),
                    "token_expires_at": auth_cache.get("expires_at"),
                }
            else:
                result_data = {"status": "Not Authenticated", "environment": environment_name}

        # --- Project Management ---
        elif name == "project_list":
            result_data = make_authenticated_request("GET", "/core/user/organization/projects/byOrg")
        elif name == "project_detail":
            project_id = arguments.get("project_id")
            result_data = make_authenticated_request("GET", f"/core/user/project/detail/{project_id}")

        # --- Organization Management ---
        elif name == "org_detail":
            result_data = make_authenticated_request("GET", "/core/user/organization")
        elif name == "org_members":
            result_data = make_authenticated_request("GET", "/core/user/organization/member")

        # --- Balance & Billing ---
        elif name == "balance_detail":
            project_id = arguments.get("project_id")
            result_data = make_authenticated_request("GET", f"/core/balance/accumulated/{project_id}")
        elif name == "billing_daily_cost":
            project_id = arguments.get("project_id")
            result_data = make_authenticated_request("GET", f"/core/billing/v2/daily-cost/{project_id}")
        elif name == "billing_monthly_cost":
            project_id = arguments.get("project_id")
            result_data = make_authenticated_request("GET", f"/core/billing/monthly-cost/total-billed/{project_id}")
        elif name == "billing_history":
            payload = {
                "project_id": arguments.get("project_id"),
                "month": arguments.get("month"),
                "page": arguments.get("page"),
                "limit": arguments.get("limit")
            }
            result_data = make_authenticated_request("POST", "/core/billing/v2/history", data=payload)

        # --- Kubernetes (k8s) Management ---
        elif name.startswith("k8s_"):
            resource = name.split("_")[1]  # pods, deployments, etc.
            project_id = arguments.get("project_id")
            namespace = arguments.get("namespace", "default")
            params = {"project_id": project_id, "namespace": namespace}

            endpoint_map = {
                "pods": "/core/pods",
                "deployments": "/core/deployment",
                "services": "/core/kubernetes/services",
                "configmaps": "/core/kubernetes/configmap",
                "secrets": "/core/kubernetes/secret",
            }
            endpoint = endpoint_map.get(resource)
            if endpoint:
                result_data = make_authenticated_request("GET", endpoint, params=params)
            else:
                result_data = f"Unknown k8s resource: {resource}"
                is_error = True

        # --- VM Management ---
        elif name == "vm_list":
            params = {"project_id": arguments.get("project_id")}
            result_data = make_authenticated_request("GET", "/core/virtual-machine/list/all", params=params)
        elif name == "vm_detail":
            payload = {"vm_id": arguments.get("vm_id")}
            result_data = make_authenticated_request("POST", "/core/virtual-machine/detail-vm", data=payload)
        elif name == "vm_create":
            payload = {
                "project_id": arguments.get("project_id"),
                "name": arguments.get("name"),
                "flavor_id": arguments.get("flavor_id"),
                "image_os_id": arguments.get("image_os_id"),
                "root_disk_size": arguments.get("root_disk_size"),
                "user_data": arguments.get("user_data"),
            }
            result_data = make_authenticated_request("POST", "/core/virtual-machine", data=payload)
        elif name == "vm_delete":
            payload = {"vm_id": arguments.get("vm_id")}
            result_data = make_authenticated_request("POST", "/core/virtual-machine/delete", data=payload)
        elif name == "vm_reboot":
            payload = {"vm_id": arguments.get("vm_id")}
            result_data = make_authenticated_request("POST", "/core/virtual-machine/reboot", data=payload)
        elif name == "vm_turn_on":
            payload = {"vm_id": arguments.get("vm_id")}
            result_data = make_authenticated_request("POST", "/core/virtual-machine/turn-on/vm", data=payload)
        elif name == "vm_turn_off":
            payload = {"vm_id": arguments.get("vm_id")}
            result_data = make_authenticated_request("POST", "/core/virtual-machine/turn-off/vm", data=payload)

        # --- Container Registry ---
        elif name == "registry_list":
            params = {"project_id": arguments.get("project_id")}
            result_data = make_authenticated_request("GET", "/core/dekaregistry/v2/registry", params=params)
        elif name == "registry_repositories":
            params = {"registry_id": arguments.get("registry_id")}
            result_data = make_authenticated_request("GET", "/core/dekaregistry/v2/repository", params=params)

        # --- Deka Notebooks ---
        elif name == "notebook_list":
            params = {"project_id": arguments.get("project_id")}
            result_data = make_authenticated_request("GET", "/core/deka-notebook", params=params)
        elif name == "notebook_create":
            payload = {
                "project_id": arguments.get("project_id"),
                "name": arguments.get("name"),
                "image": arguments.get("image"),
                "flavor_id": arguments.get("flavor_id"),
            }
            result_data = make_authenticated_request("POST", "/core/deka-notebook", data=payload)

        # --- Voucher Management ---
        elif name == "voucher_list":
            result_data = make_authenticated_request("GET", "/core/user/voucher-credit/claimed")
        elif name == "voucher_apply":
            payload = {"voucher_code": arguments.get("voucher_code")}
            result_data = make_authenticated_request("POST", "/core/user/voucher-credit/claim", data=payload)

        # --- API Token Management ---
        elif name == "token_list":
            result_data = make_authenticated_request("GET", "/core/cldkctl/token")
        elif name == "token_create":
            payload = {
                "name": arguments.get("name"),
                "expired_at": arguments.get("expired_at")
            }
            result_data = make_authenticated_request("POST", "/core/cldkctl/token", data=payload)
        elif name == "token_delete":
            token_id = arguments.get("token_id")
            result_data = make_authenticated_request("DELETE", f"/core/cldkctl/token/{token_id}")

        # --- Utility Tools ---
        elif name == "audit_logs":
            result_data = make_authenticated_request("GET", "/core/api/v1.1/user/activity/sp/get-auditlog")

        else:
            result_data = f"Tool '{name}' not found."
            is_error = True
        
        if isinstance(result_data, dict) and result_data.get("error"):
            is_error = True

    except Exception as e:
        error_message = f"❌ API Error: {str(e)}"
        print(error_message, file=sys.stderr)
        result_data = error_message
        is_error = True
        # Attempt to extract status code for better error reporting
        if hasattr(e, 'response') and e.response is not None:
             result_data = f"❌ API Error: {e.response.status_code} {e.response.reason} for url: {e.response.url}"


    print(f"DEBUG: result_data type: {type(result_data)}", file=sys.stderr)
    print(f"DEBUG: is_error value: {is_error}", file=sys.stderr)
    # For the content list:
    content_list = [TextContent(type="text", text=format_response(result_data))]
    print(f"DEBUG: content_list: {content_list}", file=sys.stderr)
    print(f"DEBUG: content_list[0] type: {type(content_list[0])}", file=sys.stderr)
    print(f"DEBUG: content_list[0] dict: {content_list[0].dict() if hasattr(content_list[0], 'dict') else 'N/A'}", file=sys.stderr)


    text_content = TextContent(type="text", text=format_response(result_data))
    return CallToolResult(content=[text_content], isError=is_error)


async def main():
    """Main function."""
    print("Initializing server...", file=sys.stderr)
    try:
        __version__ = metadata.version("mcp-cldkctl")
    except metadata.PackageNotFoundError:
        __version__ = "0.0.0-dev"

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="cldkctl",
                server_version=__version__,
                capabilities=server.get_capabilities(
                    notification_options=SimpleNotificationOptions(
                        prompts_changed=False,
                        resources_changed=False,
                        tools_changed=False,
                    ),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutting down.", file=sys.stderr)