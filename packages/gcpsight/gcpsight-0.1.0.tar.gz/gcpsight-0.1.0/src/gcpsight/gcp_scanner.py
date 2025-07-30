# gcp_scanner.py
from google.cloud import compute_v1
from google.cloud import storage
from google.cloud import resourcemanager_v3
from google.cloud import bigquery
from google.cloud import functions_v1
from google.api_core import exceptions as google_exceptions # For error handling

def check_open_firewalls(project_id: str) -> list:
    """Scans VPC firewall rules for potential public exposure."""
    open_rules = []
    try:
        client = compute_v1.FirewallsClient()
        request = compute_v1.ListFirewallsRequest(project=project_id)
        firewalls = client.list(request=request)

        for firewall in firewalls:
            if not firewall.disabled:
                is_open_ingress = False
                if firewall.direction == compute_v1.Firewall.Direction.INGRESS.name:
                    if "0.0.0.0/0" in firewall.source_ranges:
                        is_open_ingress = True

                if is_open_ingress:
                    processed_allowed_ports = []
                    if firewall.allowed: # Ensure 'allowed' exists
                        for allow_rule_item in firewall.allowed:
                            if allow_rule_item: # Ensure the item itself is not None
                                try:
                                    # Attempt to access the fields using the casing from direct API response
                                    protocol = allow_rule_item.I_p_protocol # Corrected casing
                                    ports_list = allow_rule_item.ports
                                    ports_str = ','.join(ports_list) if ports_list else "any"
                                    processed_allowed_ports.append(f"{protocol}:{ports_str}")
                                except Exception as e_item:
                                    print(f"Warning: Could not process a firewall allow rule item for firewall '{firewall.name}'. Error: {e_item}")
                                    # Simplified debugging for unexpected errors
                                    print(f"    DEBUG: Problematic item dir: {dir(allow_rule_item)}")
                                    processed_allowed_ports.append("[Error processing item]")
                            else:
                                processed_allowed_ports.append("[Invalid None item in allowed rules]")
                    else:
                        processed_allowed_ports.append("No 'allowed' rules defined")

                    open_rules.append({
                        "name": firewall.name,
                        "network": firewall.network.split('/')[-1],
                        "source_ranges": list(firewall.source_ranges),
                        "allowed_ports": processed_allowed_ports
                    })
        return open_rules
    except google_exceptions.PermissionDenied:
         print(f"Error: Permission denied to list firewalls in project {project_id}.")
         return ["Error: Permission Denied"]
    except Exception as e:
        print(f"An unexpected error occurred checking firewalls: {e}")
        return [f"Error: {str(e)}"]

def check_public_buckets(project_id: str) -> list:
    """Checks GCS buckets for public access (allUsers or allAuthenticatedUsers)."""
    public_buckets = []
    try:
        storage_client = storage.Client(project=project_id)
        buckets = storage_client.list_buckets()

        for bucket in buckets:
            try:
                policy = bucket.get_iam_policy(requested_policy_version=3)
                is_public = False
                public_roles = []

                for binding in policy.bindings:
                    if "allUsers" in binding["members"] or "allAuthenticatedUsers" in binding["members"]:
                        is_public = True
                        public_roles.append(f"{binding['role']} for {', '.join(binding['members'])}")

                if is_public:
                    public_buckets.append({
                        "name": bucket.name,
                        "roles": public_roles
                    })
            except google_exceptions.NotFound:
                pass
            except google_exceptions.PermissionDenied:
                 print(f"Warning: Permission denied to get IAM policy for bucket {bucket.name}.")
            except Exception as e:
                 print(f"Error checking bucket {bucket.name}: {e}")
        return public_buckets
    except google_exceptions.PermissionDenied:
         print(f"Error: Permission denied to list buckets in project {project_id}.")
         return ["Error: Permission Denied"]
    except Exception as e:
        print(f"An unexpected error occurred checking buckets: {e}")
        return [f"Error: {str(e)}"]

def check_overly_permissive_iam_roles(project_id: str) -> list:
    """Checks for IAM policies that grant overly permissive roles to a wide range of members."""
    overly_permissive_bindings = []
    try:
        client = resourcemanager_v3.ProjectsClient()
        policy = client.get_iam_policy(resource=f"projects/{project_id}")
        for binding in policy.bindings:
            if binding.role in ["roles/owner", "roles/editor"] and len(binding.members) > 5:
                overly_permissive_bindings.append({
                    "role": binding.role,
                    "members": list(binding.members),
                    "member_count": len(binding.members)
                })
        return overly_permissive_bindings
    except google_exceptions.PermissionDenied:
        print(f"Error: Permission denied to get IAM policy for project {project_id}.")
        return ["Error: Permission Denied"]
    except Exception as e:
        print(f"An unexpected error occurred checking IAM policies: {e}")
        return [f"Error: {str(e)}"]

def check_public_bigquery_datasets(project_id: str) -> list:
    """Checks for BigQuery datasets with public access."""
    public_datasets = []
    try:
        client = bigquery.Client(project=project_id)
        datasets = list(client.list_datasets())
        for dataset_item in datasets:
            dataset_id = dataset_item.dataset_id
            dataset = client.get_dataset(dataset_id)
            is_public = False
            public_access_entries = []
            if dataset.access_entries:
                for entry in dataset.access_entries:
                    if entry.entity_id == "allUsers" or entry.entity_id == "allAuthenticatedUsers":
                        is_public = True
                        public_access_entries.append(f"Role: {entry.role}, Member: {entry.entity_id}")
            if is_public:
                public_datasets.append({
                    "dataset_id": dataset_id,
                    "project_id": project_id,
                    "access_entries": public_access_entries
                })
        return public_datasets
    except google_exceptions.PermissionDenied:
        print(f"Error: Permission denied to list or get BigQuery datasets in project {project_id}.")
        return ["Error: Permission Denied"]
    except Exception as e:
        print(f"An unexpected error occurred checking BigQuery datasets: {e}")
        return [f"Error: {str(e)}"]

def check_insecure_cloud_functions(project_id: str) -> list:
    """Checks for Cloud Functions with security misconfigurations."""
    insecure_functions = []
    try:
        client = functions_v1.CloudFunctionsServiceClient()
        
        # Try a more comprehensive approach to find functions
        # Start with the most common regions where functions are deployed
        regions_to_check = [
            "us-central1", "us-east1", "us-east4", "us-west1", "us-west2", "us-west3", "us-west4",
            "europe-west1", "europe-west2", "europe-west3", "europe-west4", "europe-west6", "europe-central2",
            "asia-east1", "asia-east2", "asia-northeast1", "asia-northeast2", "asia-northeast3",
            "asia-south1", "asia-southeast1", "asia-southeast2", "australia-southeast1", "australia-southeast2"
        ]
        
        all_functions = []
        checked_locations = 0
        
        for location in regions_to_check:
            try:
                parent = f"projects/{project_id}/locations/{location}"
                
                # Try different approaches for the API call
                try:
                    # Method 1: Direct parent parameter (older API style)
                    page_result = client.list_functions(parent=parent)
                except TypeError:
                    # Method 2: With request object (newer API style)
                    request = functions_v1.ListFunctionsRequest(parent=parent)
                    page_result = client.list_functions(request=request)
                
                function_count = 0
                for function in page_result:
                    all_functions.append(function)
                    function_count += 1
                
                if function_count > 0:
                    print(f"Found {function_count} Cloud Functions in {location}")
                
                checked_locations += 1
                
            except google_exceptions.NotFound:
                # No functions in this location or location doesn't exist
                continue
            except google_exceptions.PermissionDenied:
                print(f"Warning: Permission denied to list Cloud Functions in {location}")
                continue
            except Exception as e:
                # Skip this location and continue
                continue
        
        print(f"Checked {checked_locations} locations, found {len(all_functions)} total functions")
        
        if not all_functions:
            return []
        
        for function in all_functions:
            security_issues = []
            function_info = {
                "name": function.name.split('/')[-1],
                "location": function.name.split('/')[3],
                "trigger_type": "Unknown",
                "security_issues": [],
                "runtime": getattr(function, 'runtime', 'Unknown'),
                "status": function.status.name if hasattr(function.status, 'name') else str(function.status)
            }
            
            # Check trigger type
            if function.https_trigger:
                function_info["trigger_type"] = "HTTPS"
                
                # Check if function allows unauthenticated invocations
                try:
                    # Get IAM policy for the function using the simpler method
                    policy = client.get_iam_policy(resource=function.name)
                    
                    for binding in policy.bindings:
                        if "allUsers" in binding.members:
                            security_issues.append("Public access - allows unauthenticated invocations")
                        if "allAuthenticatedUsers" in binding.members:
                            security_issues.append("Allows any authenticated user to invoke")
                        if "roles/cloudfunctions.invoker" in binding.role and len(binding.members) > 10:
                            security_issues.append(f"Overly broad invoker permissions ({len(binding.members)} members)")
                            
                except google_exceptions.PermissionDenied:
                    security_issues.append("Unable to check IAM policy - insufficient permissions")
                except Exception as e:
                    # Skip IAM check if it fails, but continue with other checks
                    pass
                    
            elif function.event_trigger:
                function_info["trigger_type"] = f"Event: {function.event_trigger.event_type}"
            
            # Check for insecure runtime versions
            runtime = function_info.get("runtime", "").lower()
            if any(old_version in runtime for old_version in ["python37", "nodejs10", "nodejs12", "go111", "java11"]):
                security_issues.append(f"Outdated runtime version: {function_info['runtime']}")
            
            # Check environment variables for potential secrets (basic check)
            if hasattr(function, 'environment_variables') and function.environment_variables:
                for key, value in function.environment_variables.items():
                    if any(secret_indicator in key.lower() for secret_indicator in ["password", "secret", "key", "token", "api_key"]):
                        if len(value) > 20:  # Likely a real secret, not a placeholder
                            security_issues.append(f"Potential secret in environment variable: {key}")
            
            # Check source repository for public access (basic check)
            if hasattr(function, 'source_archive_url') and function.source_archive_url:
                if "public" in function.source_archive_url.lower():
                    security_issues.append("Function source may be publicly accessible")
            
            # Check for VPC connector security
            if hasattr(function, 'vpc_connector') and function.vpc_connector:
                # This is generally good for security, but we note it for completeness
                pass
            else:
                if function_info["trigger_type"] == "HTTPS":
                    security_issues.append("No VPC connector - function has direct internet access")
            
            function_info["security_issues"] = security_issues
            
            # Only include functions with security issues
            if security_issues:
                insecure_functions.append(function_info)
                
        return insecure_functions
        
    except google_exceptions.PermissionDenied:
        print(f"Error: Permission denied to list Cloud Functions in project {project_id}.")
        return ["Error: Permission Denied"]
    except Exception as e:
        print(f"An unexpected error occurred checking Cloud Functions: {e}")
        return [f"Error: {str(e)}"]
