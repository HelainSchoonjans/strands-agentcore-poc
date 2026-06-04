import json

# Define the core ticketing paths your Strands agent actually needs
ALLOWED_PATHS = [
    "/rest/api/3/issue",
    "/rest/api/3/issue/{issueIdOrKey}",
    "/rest/api/3/issue/{issueIdOrKey}/comment",
    "/rest/api/3/search"
]
ALLOWED_MEDIA_TYPES = ["application/json", "application/xml", "multipart/form-data", "application/x-www-form-urlencoded"]

with open("jira-spec.json", "r") as f:
    spec = json.load(f)

# 1. Filter down to essential paths
clean_paths = {}
for path, methods in spec.get("paths", {}).items():
    if path in ALLOWED_PATHS:
        clean_methods = {}
        for method, op_data in methods.items():
            
            # 2. Clean Request Body Media Types
            if "requestBody" in op_data and "content" in op_data["requestBody"]:
                content = op_data["requestBody"]["content"]
                op_data["requestBody"]["content"] = {
                    k: v for k, v in content.items() if k in ALLOWED_MEDIA_TYPES
                }
                # Fallback if we stripped everything
                if not op_data["requestBody"]["content"]:
                    continue
            
            # 3. Clean Response Media Types
            if "responses" in op_data:
                for code, resp_data in op_data["responses"].items():
                    if "content" in resp_data:
                        resp_data["content"] = {
                            k: v for k, v in resp_data["content"].items() if k in ALLOWED_MEDIA_TYPES
                        }
            
            clean_methods[method] = op_data
        if clean_methods:
            clean_paths[path] = clean_methods

spec["paths"] = clean_paths

# Write out the pristine, AWS-compliant schema
with open("swagger-v3.v3.json", "w") as f:
    json.dump(spec, f, indent=2)

print("Success! Generated 'jira-spec-clean.json'. Re-run your gateway target creation now.")