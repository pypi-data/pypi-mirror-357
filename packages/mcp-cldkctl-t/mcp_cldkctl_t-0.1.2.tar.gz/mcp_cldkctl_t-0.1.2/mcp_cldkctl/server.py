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
    """Get all tool definitions."""
    tools = [
        # Authentication tools (keep existing ones)
        Tool(
            name="auth",
            description="Authenticate with a cldkctl token to get JWT access",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "Your cldkctl token (starts with 'cldkctl_')"
                    },
                    "force_staging": {
                        "type": "boolean",
                        "description": "Force using staging environment (default: false, will auto-fallback if production fails)"
                    }
                },
                "required": ["token"]
            }
        ),
        
        Tool(
            name="switch_environment",
            description="Switch between production and staging environments",
            inputSchema={
                "type": "object",
                "properties": {
                    "environment": {
                        "type": "string",
                        "description": "Environment to use: 'production' or 'staging'",
                        "enum": ["production", "staging"]
                    }
                },
                "required": ["environment"]
            }
        ),
        
        Tool(
            name="status",
            description="Show current authentication and environment status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        # User & Profile Management
        Tool(
            name="profile_detail",
            description="Get user profile details",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="update_profile",
            description="Update user profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to update"
                    },
                    "profile_data": {
                        "type": "object",
                        "description": "Profile data to update"
                    }
                },
                "required": ["user_id", "profile_data"]
            }
        ),

        Tool(
            name="change_password",
            description="Change user password",
            inputSchema={
                "type": "object",
                "properties": {
                    "old_password": {
                        "type": "string",
                        "description": "Current password"
                    },
                    "new_password": {
                        "type": "string",
                        "description": "New password"
                    }
                },
                "required": ["old_password", "new_password"]
            }
        ),

        # Project Management
        Tool(
            name="project_list",
            description="List all projects in the organization",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="project_detail",
            description="Get details of a specific project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),

        Tool(
            name="update_project",
            description="Update project details",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "project_data": {
                        "type": "object",
                        "description": "Project data to update"
                    }
                },
                "required": ["project_id", "project_data"]
            }
        ),

        Tool(
            name="delete_project",
            description="Delete a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),

        # Organization Management
        Tool(
            name="org_detail",
            description="Get organization details",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="org_edit",
            description="Edit organization details",
            inputSchema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID"
                    },
                    "org_data": {
                        "type": "object",
                        "description": "Organization data to update"
                    }
                },
                "required": ["organization_id", "org_data"]
            }
        ),

        Tool(
            name="org_members",
            description="List organization members",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="org_member_add",
            description="Add a member to the organization",
            inputSchema={
                "type": "object",
                "properties": {
                    "member_data": {
                        "type": "object",
                        "description": "Member data including email and role"
                    }
                },
                "required": ["member_data"]
            }
        ),

        Tool(
            name="org_member_edit",
            description="Edit organization member",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    },
                    "member_data": {
                        "type": "object",
                        "description": "Member data to update"
                    }
                },
                "required": ["user_id", "member_data"]
            }
        ),

        Tool(
            name="org_member_delete",
            description="Delete organization member",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID to delete"
                    }
                },
                "required": ["user_id"]
            }
        ),

        # Balance & Billing
        Tool(
            name="balance_detail",
            description="Get balance details for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="billing_daily_cost",
            description="Get daily billing costs for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="billing_monthly_cost",
            description="Get monthly billing costs for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="billing_history",
            description="Get billing history",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID (optional)"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    }
                }
            }
        ),
        
        Tool(
            name="billing_invoice_sme",
            description="Get SME billing invoices",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="billing_invoice_sme_detail",
            description="Get SME billing invoice details",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "Invoice ID"
                    }
                },
                "required": ["invoice_id"]
            }
        ),

        Tool(
            name="billing_invoice_enterprise",
            description="Get enterprise billing invoices",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),

        # Kubernetes Core Resources
        Tool(
            name="k8s_pods",
            description="List Kubernetes pods in a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace (default: 'default')"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="k8s_pod_create",
            description="Create a new pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "pod_spec": {
                        "type": "object",
                        "description": "Pod specification"
                    }
                },
                "required": ["project_id", "namespace", "pod_spec"]
            }
        ),
        
        Tool(
            name="k8s_pod_edit",
            description="Edit an existing pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "name": {
                        "type": "string",
                        "description": "Pod name"
                    },
                    "pod_spec": {
                        "type": "object",
                        "description": "Updated pod specification"
                    }
                },
                "required": ["project_id", "namespace", "name", "pod_spec"]
            }
        ),
        
        Tool(
            name="k8s_pod_delete",
            description="Delete a pod",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "name": {
                        "type": "string",
                        "description": "Pod name"
                    }
                },
                "required": ["project_id", "namespace", "name"]
            }
        ),
        
        Tool(
            name="k8s_pod_console",
            description="Get pod console access",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "Console access token"
                    }
                },
                "required": ["token"]
            }
        ),

        Tool(
            name="k8s_pod_console_token",
            description="Get pod console access token",
            inputSchema={
                "type": "object",
                "properties": {
                    "pod_name": {
                        "type": "string",
                        "description": "Pod name"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    }
                },
                "required": ["pod_name", "namespace"]
            }
        ),

        # Kubernetes Deployments
        Tool(
            name="k8s_deployments",
            description="List Kubernetes deployments",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace (default: 'default')"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="k8s_deployment_create",
            description="Create a new Kubernetes deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "deployment_spec": {
                        "type": "object",
                        "description": "Deployment specification"
                    }
                },
                "required": ["project_id", "namespace", "deployment_spec"]
            }
        ),
        
        Tool(
            name="k8s_deployment_edit",
            description="Edit a Kubernetes deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "name": {
                        "type": "string",
                        "description": "Deployment name"
                    },
                    "deployment_spec": {
                        "type": "object",
                        "description": "Updated deployment specification"
                    }
                },
                "required": ["project_id", "namespace", "name", "deployment_spec"]
            }
        ),

        Tool(
            name="k8s_deployment_delete",
            description="Delete a Kubernetes deployment",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "name": {
                        "type": "string",
                        "description": "Deployment name"
                    }
                },
                "required": ["project_id", "namespace", "name"]
            }
        ),

        # Kubernetes Services
        Tool(
            name="k8s_services",
            description="List Kubernetes services in a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace (default: 'default')"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="k8s_configmaps",
            description="List Kubernetes configmaps in a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace (default: 'default')"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="k8s_secrets",
            description="List Kubernetes secrets in a namespace",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace (default: 'default')"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        # Virtual Machines
        Tool(
            name="vm_list",
            description="List virtual machines",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="vm_create",
            description="Create a new virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_spec": {
                        "type": "object",
                        "description": "Virtual machine specification"
                    }
                },
                "required": ["vm_spec"]
            }
        ),
        
        Tool(
            name="vm_detail",
            description="Get virtual machine details",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "vm_id": {
                        "type": "string",
                        "description": "Virtual Machine ID"
                    }
                },
                "required": ["project_id", "vm_id"]
            }
        ),
        
        Tool(
            name="vm_delete",
            description="Delete a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_data": {
                        "type": "object",
                        "description": "VM deletion data"
                    }
                },
                "required": ["vm_data"]
            }
        ),
        
        Tool(
            name="vm_reboot",
            description="Reboot a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_data": {
                        "type": "object",
                        "description": "VM reboot data"
                    }
                },
                "required": ["vm_data"]
            }
        ),
        
        Tool(
            name="vm_turn_off",
            description="Turn off a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_data": {
                        "type": "object",
                        "description": "VM turn off data"
                    }
                },
                "required": ["vm_data"]
            }
        ),
        
        Tool(
            name="vm_turn_on",
            description="Turn on a virtual machine",
            inputSchema={
                "type": "object",
                "properties": {
                    "vm_data": {
                        "type": "object",
                        "description": "VM turn on data"
                    }
                },
                "required": ["vm_data"]
            }
        ),
        
        # Registry
        Tool(
            name="registry_list",
            description="List container registries",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Items per page (optional)"
                    }
                },
                "required": ["project_id"]
            }
        ),
        
        Tool(
            name="registry_create",
            description="Create a new registry",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_data": {
                        "type": "object",
                        "description": "Registry creation data"
                    }
                },
                "required": ["registry_data"]
            }
        ),
        
        Tool(
            name="registry_update",
            description="Update registry details",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    },
                    "registry_data": {
                        "type": "object",
                        "description": "Registry update data"
                    }
                },
                "required": ["registry_id", "registry_data"]
            }
        ),
        
        Tool(
            name="registry_detail",
            description="Get registry details",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    }
                },
                "required": ["registry_id"]
            }
        ),
        
        Tool(
            name="registry_repositories",
            description="List repositories in a registry",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Items per page (optional)"
                    }
                },
                "required": ["registry_id"]
            }
        ),
        
        # Notebooks
        Tool(
            name="notebook_list",
            description="List Deka notebooks",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        Tool(
            name="notebook_create",
            description="Create a new Deka notebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Notebook name"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "image": {
                        "type": "string",
                        "description": "Docker image to use"
                    },
                    "cpu": {
                        "type": "string",
                        "description": "CPU specification (e.g., '1')"
                    },
                    "memory": {
                        "type": "string",
                        "description": "Memory specification (e.g., '2Gi')"
                    },
                    "gpu": {
                        "type": "string",
                        "description": "GPU specification (optional)"
                    }
                },
                "required": ["name", "project_id", "image", "cpu", "memory"]
            }
        ),
        
        Tool(
            name="notebook_delete",
            description="Delete a Deka notebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "notebook_id": {
                        "type": "string",
                        "description": "Notebook ID"
                    }
                },
                "required": ["notebook_id"]
            }
        ),

        Tool(
            name="notebook_update",
            description="Update a Deka notebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "notebook_id": {
                        "type": "string",
                        "description": "Notebook ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "New notebook name"
                    },
                    "image": {
                        "type": "string",
                        "description": "New Docker image"
                    },
                    "cpu": {
                        "type": "string",
                        "description": "New CPU specification"
                    },
                    "memory": {
                        "type": "string",
                        "description": "New memory specification"
                    },
                    "gpu": {
                        "type": "string",
                        "description": "New GPU specification (optional)"
                    }
                },
                "required": ["notebook_id"]
            }
        ),

        Tool(
            name="notebook_start",
            description="Start a Deka notebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "notebook_id": {
                        "type": "string",
                        "description": "Notebook ID"
                    }
                },
                "required": ["notebook_id"]
            }
        ),

        Tool(
            name="notebook_stop",
            description="Stop a Deka notebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "notebook_id": {
                        "type": "string",
                        "description": "Notebook ID"
                    }
                },
                "required": ["notebook_id"]
            }
        ),

        Tool(
            name="notebook_images",
            description="List available notebook images",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        # Registry Additional Operations
        Tool(
            name="registry_overview",
            description="Get registry overview",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    }
                },
                "required": ["registry_id"]
            }
        ),

        Tool(
            name="registry_cert",
            description="Download registry certificate",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="registry_logs",
            description="Get registry logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    }
                },
                "required": ["registry_id"]
            }
        ),

        # Registry Labels
        Tool(
            name="registry_labels",
            description="List registry labels",
            inputSchema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    }
                },
                "required": ["organization_id", "user_id", "project_id", "registry_id"]
            }
        ),

        Tool(
            name="registry_labels_update",
            description="Update registry labels",
            inputSchema={
                "type": "object",
                "properties": {
                    "organization_id": {
                        "type": "string",
                        "description": "Organization ID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    },
                    "labels_data": {
                        "type": "object",
                        "description": "Labels update data"
                    }
                },
                "required": ["organization_id", "user_id", "project_id", "registry_id", "labels_data"]
            }
        ),
        
        # Vouchers
        Tool(
            name="voucher_list",
            description="List available vouchers",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        Tool(
            name="voucher_apply",
            description="Apply a voucher code",
            inputSchema={
                "type": "object",
                "properties": {
                    "voucher_code": {
                        "type": "string",
                        "description": "Voucher code to apply"
                    }
                },
                "required": ["voucher_code"]
            }
        ),
        
        # Logs
        Tool(
            name="audit_logs",
            description="Get audit logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (YYYY-MM-DD)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (YYYY-MM-DD)"
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Items per page (optional)"
                    },
                    "action_type": {
                        "type": "string",
                        "description": "Filter by action type (optional)"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        
        # Token Management
        Tool(
            name="token_list",
            description="List cldkctl tokens",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        
        Tool(
            name="token_create",
            description="Create a new cldkctl token",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Token name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Token description (optional)"
                    },
                    "expiration_days": {
                        "type": "integer",
                        "description": "Token expiration in days"
                    }
                },
                "required": ["name", "expiration_days"]
            }
        ),
        
        Tool(
            name="token_delete",
            description="Delete a cldkctl token",
            inputSchema={
                "type": "object",
                "properties": {
                    "token_id": {
                        "type": "string",
                        "description": "Token ID to delete"
                    }
                },
                "required": ["token_id"]
            }
        ),

        # Additional Kubernetes Tools
        Tool(
            name="k8s_service_create",
            description="Create a new Kubernetes service",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "service_spec": {
                        "type": "object",
                        "description": "Service specification"
                    }
                },
                "required": ["project_id", "namespace", "service_spec"]
            }
        ),

        Tool(
            name="k8s_service_edit",
            description="Edit a Kubernetes service",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "name": {
                        "type": "string",
                        "description": "Service name"
                    },
                    "service_spec": {
                        "type": "object",
                        "description": "Updated service specification"
                    }
                },
                "required": ["project_id", "namespace", "name", "service_spec"]
            }
        ),

        Tool(
            name="k8s_service_delete",
            description="Delete a Kubernetes service",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "name": {
                        "type": "string",
                        "description": "Service name"
                    }
                },
                "required": ["project_id", "namespace", "name"]
            }
        ),

        # Registry Tag Management
        Tool(
            name="registry_tag_list",
            description="List registry tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    }
                },
                "required": ["registry_id"]
            }
        ),

        Tool(
            name="registry_tag_create",
            description="Create a registry tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    },
                    "tag_data": {
                        "type": "object",
                        "description": "Tag creation data"
                    }
                },
                "required": ["registry_id", "tag_data"]
            }
        ),

        Tool(
            name="registry_tag_update",
            description="Update a registry tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_id": {
                        "type": "string",
                        "description": "Tag ID"
                    },
                    "tag_data": {
                        "type": "object",
                        "description": "Tag update data"
                    }
                },
                "required": ["tag_id", "tag_data"]
            }
        ),

        Tool(
            name="registry_tag_delete",
            description="Delete a registry tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_id": {
                        "type": "string",
                        "description": "Tag ID"
                    }
                },
                "required": ["tag_id"]
            }
        ),

        Tool(
            name="registry_tag_disable",
            description="Disable a registry tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_id": {
                        "type": "string",
                        "description": "Tag ID"
                    }
                },
                "required": ["tag_id"]
            }
        ),

        Tool(
            name="registry_tag_enable",
            description="Enable a registry tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag_id": {
                        "type": "string",
                        "description": "Tag ID"
                    }
                },
                "required": ["tag_id"]
            }
        ),

        # Registry Member Management
        Tool(
            name="registry_member_list",
            description="List registry members",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    }
                },
                "required": ["registry_id"]
            }
        ),

        Tool(
            name="registry_available_member",
            description="List available members for registry",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),

        Tool(
            name="registry_show_password",
            description="Show registry user password",
            inputSchema={
                "type": "object",
                "properties": {
                    "password_data": {
                        "type": "object",
                        "description": "Password request data"
                    }
                },
                "required": ["password_data"]
            }
        ),

        Tool(
            name="registry_member_add",
            description="Add a member to registry",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    },
                    "member_data": {
                        "type": "object",
                        "description": "Member data"
                    }
                },
                "required": ["registry_id", "member_data"]
            }
        ),

        Tool(
            name="registry_member_delete",
            description="Delete a member from registry",
            inputSchema={
                "type": "object",
                "properties": {
                    "registry_id": {
                        "type": "string",
                        "description": "Registry ID"
                    },
                    "member_id": {
                        "type": "string",
                        "description": "Member ID"
                    }
                },
                "required": ["registry_id", "member_id"]
            }
        ),

        # Registry Artifact Management
        Tool(
            name="registry_artifact_list",
            description="List registry artifacts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="registry_artifact_detail",
            description="Get artifact details",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    }
                },
                "required": ["artifact_id"]
            }
        ),

        Tool(
            name="registry_artifact_add_label",
            description="Add label to artifact",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    },
                    "label_id": {
                        "type": "string",
                        "description": "Label ID"
                    }
                },
                "required": ["artifact_id", "label_id"]
            }
        ),

        Tool(
            name="registry_artifact_remove_label",
            description="Remove label from artifact",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    },
                    "label_id": {
                        "type": "string",
                        "description": "Label ID"
                    }
                },
                "required": ["artifact_id", "label_id"]
            }
        ),

        Tool(
            name="registry_artifact_scan",
            description="Scan an artifact",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    }
                },
                "required": ["artifact_id"]
            }
        ),

        Tool(
            name="registry_artifact_stop_scan",
            description="Stop artifact scan",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    }
                },
                "required": ["artifact_id"]
            }
        ),

        Tool(
            name="registry_artifact_tags",
            description="List artifact tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    }
                },
                "required": ["artifact_id"]
            }
        ),

        Tool(
            name="registry_artifact_delete_tag",
            description="Delete artifact tag",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Tag name"
                    }
                },
                "required": ["artifact_id", "tag"]
            }
        ),

        Tool(
            name="registry_artifact_add_tag",
            description="Add tag to artifact",
            inputSchema={
                "type": "object",
                "properties": {
                    "artifact_id": {
                        "type": "string",
                        "description": "Artifact ID"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Tag name"
                    }
                },
                "required": ["artifact_id", "tag"]
            }
        ),

        # Organization Member Management
        Tool(
            name="org_member_activate",
            description="Activate an organization member",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    }
                },
                "required": ["user_id"]
            }
        ),

        Tool(
            name="org_member_deactivate",
            description="Deactivate an organization member",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    }
                },
                "required": ["user_id"]
            }
        ),

        Tool(
            name="org_member_resend_invitation",
            description="Resend invitation to organization member",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User ID"
                    }
                },
                "required": ["user_id"]
            }
        ),

        # VM Additional Operations
        Tool(
            name="vm_create_yaml",
            description="Create a virtual machine from YAML",
            inputSchema={
                "type": "object",
                "properties": {
                    "yaml_data": {
                        "type": "object",
                        "description": "VM YAML specification"
                    }
                },
                "required": ["yaml_data"]
            }
        ),

        Tool(
            name="vm_edit_yaml",
            description="Edit a virtual machine using YAML",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    },
                    "namespace": {
                        "type": "string",
                        "description": "Namespace"
                    },
                    "name": {
                        "type": "string",
                        "description": "VM name"
                    },
                    "yaml_data": {
                        "type": "object",
                        "description": "Updated VM YAML specification"
                    }
                },
                "required": ["project_id", "namespace", "name", "yaml_data"]
            }
        ),

        Tool(
            name="vm_image_os",
            description="List available VM OS images",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="vm_flavor_type",
            description="List available VM flavor types",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        Tool(
            name="vm_gpu",
            description="List available GPU options for VMs",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),

        Tool(
            name="vm_storage_class",
            description="List available storage classes for VMs",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {
                        "type": "string",
                        "description": "Project ID"
                    }
                },
                "required": ["project_id"]
            }
        ),

        Tool(
            name="vm_flavor",
            description="List available VM flavors by type",
            inputSchema={
                "type": "object",
                "properties": {
                    "flavorType_id": {
                        "type": "string",
                        "description": "Flavor Type ID"
                    }
                },
                "required": ["flavorType_id"]
            }
        ),
    ]
    return tools


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools."""
    try:
        tools = get_tool_definitions()
        print(f"Successfully loaded {len(tools)} tools.", file=sys.stderr)
        return tools
    except Exception as e:
        print(f"!!!!!!!! ERROR GETTING TOOL DEFINITIONS !!!!!!!!", file=sys.stderr)
        print(f"Exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return []


def format_response(data: Any) -> str:
    """Formats API response data for display."""
    if isinstance(data, dict) and data.get("error"):
        return f"❌ API Error: {data.get('message', 'Unknown error')}"
    return f"```json\n{json.dumps(data, indent=2)}\n```"


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[Content]:
    """Handle tool calls."""
    global current_base_url, environment_name
    
    try:
        # Handle authentication tools
        if name == "auth":
            token = arguments["token"]
            force_staging = arguments.get("force_staging", False)
            if authenticate_with_token(token, force_staging):
                env_info = f" ({environment_name})" if environment_name != "production" else ""
                user_info = auth_cache.get('user_info', {})
                text = (
                    f"✅ Authentication successful{env_info}!\n\n"
                    f"User: {user_info.get('name', 'Unknown')}\n"
                    f"Role: {user_info.get('role', 'Unknown')}\n"
                    f"Organization: {user_info.get('organization_id', 'None')}\n"
                    f"Environment: {environment_name}\n"
                    f"Base URL: {current_base_url}"
                )
                return [TextContent(type="text", text=text)]
            else:
                return [TextContent(type="text", text="❌ Authentication failed.")]

        elif name == "switch_environment":
            env = arguments["environment"]
            if env in ["production", "staging"]:
                current_base_url = PRODUCTION_URL if env == "production" else STAGING_URL
                environment_name = env
                auth_cache.update({"jwt_token": None, "expires_at": None, "environment": env, "base_url": current_base_url})
                save_cache()
                text = f"✅ Switched to {environment_name} environment. You may need to re-authenticate."
            else:
                text = "❌ Invalid environment. Use 'production' or 'staging'."
            return [TextContent(type="text", text=text)]

        elif name == "status":
            status_text = f"**Environment Status**\n- **Environment:** {environment_name}\n- **Base URL:** {current_base_url}\n\n"
            if auth_cache.get("jwt_token"):
                expires_at = datetime.fromisoformat(auth_cache["expires_at"]) if auth_cache["expires_at"] else None
                status_text += f"**Authentication Status**\n- **Status:** ✅ Authenticated\n"
                status_text += f"- **User:** {auth_cache.get('user_info', {}).get('name', 'Unknown')}\n"
                if expires_at:
                    status_text += f"- **Token Expires:** {expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                status_text += f"**Authentication Status**\n- **Status:** ❌ Not authenticated"
            return [TextContent(type="text", text=status_text)]

        # Generic handler for API endpoints
        endpoint_map = {
            # --- User & Profile ---
            "profile_detail": "/core/user/profile",
            "update_profile": ("/core/user/organization/profile/member/{user_id}", "PUT"),
            "change_password": ("/core/user/change-password", "POST"),

            # --- Projects ---
            "project_list": "/core/user/organization/projects/byOrg",
            "project_detail": "/core/user/project/detail/{project_id}",
            "update_project": ("/core/user/projects/{project_id}", "PUT"),
            "delete_project": ("/core/user/projects/{project_id}", "DELETE"),
            "check_before_delete_project": ("/core/user/checking/projects/{project_id}", "DELETE"),

            # --- Organization ---
            "org_detail": "/core/user/organization",
            "org_edit": ("/core/user/organization/edit/{organization_id}", "PUT"),
            "org_members": "/core/user/organization/member",
            "org_member_add": ("/core/user/organization/member", "POST"),
            "org_member_edit": ("/core/user/organization/member/{user_id}", "PUT"),
            "org_member_delete": ("/core/user/organization/member/{user_id}", "DELETE"),
            "org_member_activate": ("/core/user/manageuser/active/{user_id}", "PUT"),
            "org_member_deactivate": ("/core/user/manageuser/deactive/{user_id}", "PUT"),
            "org_member_resend_invitation": ("/core/superadmin/manageuser/resend-verified/{user_id}", "POST"),

            # --- Balance & Billing ---
            "balance_detail": "/core/balance/accumulated/{project_id}",
            "billing_daily_cost": "/core/billing/v2/daily-cost/{project_id}",
            "billing_monthly_cost": "/core/billing/monthly-cost/total-billed/{project_id}",
            "billing_history": ("/core/billing/v2/history", "POST"),
            "billing_invoice_sme": "/core/balance/history/invoice",
            "billing_invoice_sme_detail": "/core/balance/history/invoice/detail/{invoice_id}",
            "billing_invoice_enterprise": "/core/billing/invoice/{project_id}",
            "billing_invoice_enterprise_detail": "/core/billing/v2/invoice/detail/{invoice_id}",
            "billing_summary": "/core/billing/{organization_id}/{project_id}/summary/monthly",
            "billing_summary_detail": "/core/billing/v2/summary/monthly/{summary_id}",

            # --- Kubernetes ---
            "k8s_pods": "/core/pods",
            "k8s_pod_create": ("/core/pods", "POST"),
            "k8s_pod_edit": ("/core/pods/{project_id}/{namespace}/{name}", "PUT"),
            "k8s_pod_delete": ("/core/pods/{project_id}/{namespace}/{name}", "DELETE"),
            "k8s_pod_console": "/core/pods/console/{token}",
            "k8s_pod_console_token": ("/core/pods/console", "POST"),

            "k8s_deployments": "/core/deployment",
            "k8s_deployment_create": ("/core/deployment", "POST"),
            "k8s_deployment_edit": ("/core/deployment/{project_id}/{namespace}/{name}", "PUT"),
            "k8s_deployment_delete": ("/core/deployment/{project_id}/{namespace}/{name}", "DELETE"),

            "k8s_services": "/core/kubernetes/services",
            "k8s_service_create": ("/core/kubernetes/services", "POST"),
            "k8s_service_edit": ("/core/kubernetes/services/{project_id}/{namespace}/{name}", "PUT"),
            "k8s_service_delete": ("/core/kubernetes/services/{project_id}/{namespace}/{name}", "DELETE"),

            "k8s_configmaps": "/core/kubernetes/configmap",
            "k8s_configmap_create": ("/core/kubernetes/configmap", "POST"),
            "k8s_configmap_edit": ("/core/kubernetes/configmap/{project_id}/{namespace}/{name}", "PUT"),
            "k8s_configmap_delete": ("/core/kubernetes/configmap/{project_id}/{namespace}/{name}", "DELETE"),

            "k8s_secrets": "/core/kubernetes/secret",
            "k8s_secret_create": ("/core/kubernetes/secret", "POST"),
            "k8s_secret_edit": ("/core/kubernetes/secret/{project_id}/{namespace}/{name}", "PUT"),
            "k8s_secret_delete": ("/core/kubernetes/secret/{project_id}/{namespace}/{name}", "DELETE"),

            # --- Virtual Machines ---
            "vm_list": "/core/virtual-machine/list/all",
            "vm_create": ("/core/virtual-machine", "POST"),
            "vm_create_yaml": ("/core/virtual-machine/yaml", "POST"),
            "vm_detail": ("/core/virtual-machine/{project_id}/{vm_id}", "GET"),
            "vm_edit_yaml": ("/core/virtual-machine/yaml/{project_id}/{namespace}/{name}", "PUT"),
            "vm_delete": ("/core/virtual-machine/{project_id}/{vm_id}", "DELETE"),
            "vm_reboot": ("/core/virtual-machine/{project_id}/{vm_id}/reboot", "POST"),
            "vm_turn_off": ("/core/virtual-machine/{project_id}/{vm_id}/stop", "POST"),
            "vm_turn_on": ("/core/virtual-machine/{project_id}/{vm_id}/start", "POST"),
            "vm_image_os": "/core/cluster-image-os",
            "vm_flavor_type": "/core/virtual-machine/flavor_type",
            "vm_gpu": "/core/virtual-machine/gpu/{project_id}",
            "vm_storage_class": "/core/virtual-machine/storage-class/{project_id}",
            "vm_flavor": "/core/virtual-machine/flavor/{flavorType_id}",

            # --- Registry ---
            "registry_list": "/core/dekaregistry/v2/registries",
            "registry_create": ("/core/dekaregistry/v2/registries", "POST"),
            "registry_update": ("/core/dekaregistry/v2/registries/{registry_id}", "PUT"),
            "registry_detail": "/core/dekaregistry/v2/registries/{registry_id}",
            "registry_overview": "/core/dekaregistry/v2/registries/{registry_id}/overview",
            "registry_cert": "/core/dekaregistry/v2/registry/cert",
            "registry_logs": "/core/dekaregistry/v2/registries/{registry_id}/logs",
            "registry_repositories": "/core/dekaregistry/v2/repositories/{registry_id}",

            # --- Notebooks ---
            "notebook_list": "/core/deka-notebook/list",
            "notebook_create": ("/core/deka-notebook/create", "POST"),
            "notebook_delete": ("/core/deka-notebook/{notebook_id}", "DELETE"),
            "notebook_update": ("/core/deka-notebook/{notebook_id}", "PUT"),
            "notebook_start": ("/core/deka-notebook/{notebook_id}/start", "POST"),
            "notebook_stop": ("/core/deka-notebook/{notebook_id}/stop", "POST"),
            "notebook_images": "/core/deka-notebook/images",

            # --- Audit Logs ---
            "audit_logs": "/core/audit/logs",

            # --- Token Management ---
            "token_list": "/core/cldkctl/tokens",
            "token_create": ("/core/cldkctl/tokens", "POST"),
            "token_delete": ("/core/cldkctl/tokens/{token_id}", "DELETE"),
            "token_update": ("/core/cldkctl/tokens/{token_id}", "PUT"),
            "token_regenerate": ("/core/cldkctl/tokens/{token_id}/regenerate", "POST"),
        }

        # Handle generic handler for API endpoints
        if name in endpoint_map:
            mapping = endpoint_map[name]
            method = "GET"
            if isinstance(mapping, tuple):
                endpoint_template, method = mapping
            else:
                endpoint_template = mapping

            # Handle path parameters
            try:
                endpoint = endpoint_template.format(**arguments)
            except KeyError as e:
                return [TextContent(type="text", text=f"❌ Missing required parameter: {e}")]

            # Split parameters between path params and body/query params
            path_params = {k for k in arguments if f"{{{k}}}" in endpoint_template}
            remaining_params = {k: v for k, v in arguments.items() if k not in path_params}

            # Make the request
            data = make_authenticated_request(
                method=method,
                endpoint=endpoint,
                data=remaining_params if method in ["POST", "PUT", "PATCH"] else None,
                params=remaining_params if method == "GET" else None
            )

            # Format the response
            return [TextContent(type="text", text=format_response(data))]
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        print(f"Error calling tool {name}: {e}", file=sys.stderr)
        return [TextContent(type="text", text=f"❌ Error: {str(e)}")]


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