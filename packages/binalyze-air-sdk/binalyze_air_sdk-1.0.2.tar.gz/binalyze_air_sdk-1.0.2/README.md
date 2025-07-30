# 🎉 Binalyze AIR Python SDK - Production Ready SDK

**PRODUCTION READY!** A comprehensive Python SDK for the Binalyze AIR cybersecurity platform with **extensive API coverage** across **18 modules**.

[![Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](https://github.com/binalyze/air-python-sdk)
[![API Coverage](https://img.shields.io/badge/API%20Coverage-Extensive-brightgreen)](https://github.com/binalyze/air-python-sdk)
[![Test Coverage](https://img.shields.io/badge/Tests-Real%20Tests-brightgreen)](https://github.com/binalyze/air-python-sdk)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE)

## 🏆 Comprehensive SDK Coverage

- ✅ **Core Operations**: Assets, Cases, Tasks, Acquisitions management
- ✅ **Security & Intelligence**: Triage, Authentication, Policies
- ✅ **Data Management**: Evidence, Audit logs, Baseline comparison
- ✅ **Administration**: Organizations, Users, Settings
- ✅ **Integration**: Webhooks, Event subscriptions, Interactions
- ✅ **Enterprise Ready**: Full error handling & validation
- ✅ **Performance Tested**: Response time validation

## 🚀 Complete Feature Set

### **Core Operations**

- **🔧 Acquisitions** - Forensic data collection, imaging, and evidence acquisition
- **📂 Cases** - Complete investigation workflow and collaboration
- **📊 Tasks** - Task orchestration and monitoring
- **🖥️ Assets** - Asset management, isolation, tagging, and control

### **Security & Intelligence**

- **🔍 Triage** - Threat detection, YARA rule creation, and analysis
- **🔐 Authentication** - Secure login, token management, and validation
- **📋 Policies** - Policy management, assignment, and execution
- **📈 Baseline** - System baseline comparison and monitoring

### **Data Management**

- **📚 Evidence** - Evidence storage, retrieval, and management
- **📊 Audit** - Comprehensive audit logging and analytics
- **🏷️ Auto Asset Tags** - Automated asset classification and tagging
- **📚 Evidences** - Repository management for evidence storage

### **Administration**

- **🏢 Organizations** - Multi-tenant administration and settings
- **👥 Users** - User administration and permissions
- **⚙️ Settings** - System configuration and banner management
- **🔗 Webhooks** - External system integration and triggers

### **Integration & Advanced**

- **📡 Event Subscription** - Real-time event notifications
- **💬 Interact** - Shell interaction and command execution
- **⚙️ Params** - System parameters and configuration
- **🏷️ Endpoints** - Endpoint tag management

## 📦 Installation

### **Standard Installation**

```bash
pip install binalyze-air-sdk
```

### **Development Installation**

```bash
git clone https://github.com/binalyze/air-python-sdk.git
cd air-python-sdk
pip install -r requirements.txt
pip install -e .
```

### **Requirements**

- Python 3.8+
- requests>=2.25.1
- pydantic>=2.0.0
- python-dateutil>=2.8.0
- urllib3>=1.26.0

## 🔧 Quick Start

```python
from binalyze_air import AIRClient

# Initialize client
client = AIRClient(
    host="https://your-air-instance.com",
    api_token="your-api-token",
    organization_id=0
)

# Test authentication
auth_status = client.authentication.check_status()
if auth_status.get('success'):
    print("✅ Connected to Binalyze AIR!")

# Asset Management
assets = client.assets.list()
client.assets.isolate(["endpoint-id"])
client.assets.add_tags(["endpoint-id"], ["investigation", "priority"])

# Case Management
from binalyze_air.models.cases import CreateCaseRequest
case_request = CreateCaseRequest(
    name="Security Investigation",
    description="Investigating suspicious activity",
    visibility="public-to-organization"
)
case = client.cases.create(case_request)

# Evidence Acquisition
profiles = client.acquisitions.list_profiles()
acquisition_request = {
    "case_id": case.id,
    "acquisition_profile_id": profiles[0].id,
    "filter": {
        "included_endpoint_ids": ["endpoint-id"],
        "organization_ids": [0]
    }
}
acquisition = client.acquisitions.acquire(acquisition_request)

# Triage Operations
rules = client.triage.list_rules()
validation = client.triage.validate_rule("rule content", "yara")

# Task Management
tasks = client.tasks.list()
task_assignments = client.tasks.get_assignments("task-id")

# User Management
users = client.user_management.list_users()
user_details = client.user_management.get_user("user-id")
```

## 📚 Complete API Reference

### **🔧 Acquisitions**

```python
# Profiles
client.acquisitions.list_profiles(filter_params, organization_ids, all_organizations)
client.acquisitions.get_profile(profile_id)
client.acquisitions.create_profile(request)

# Tasks
client.acquisitions.acquire(request)                    # Assign evidence task
client.acquisitions.acquire_image(request)              # Assign image task

# Legacy aliases
client.acquisitions.assign_task(request)                # Legacy alias for acquire
client.acquisitions.assign_image_task(request)          # Legacy alias for acquire_image
```

### **📂 Cases**

```python
# Case Management
client.cases.list(filter_params, organization_ids)      # List cases
client.cases.create(case_data)                          # Create case
client.cases.get(case_id)                               # Get case details
client.cases.update(case_id, update_data)               # Update case
client.cases.close(case_id)                             # Close case
client.cases.open(case_id)                              # Open case
client.cases.archive(case_id)                           # Archive case
client.cases.change_owner(case_id, user_id)             # Change owner
client.cases.check_name(name)                           # Check name availability

# Case Data
client.cases.get_activities(case_id, filter_params)     # Get activities
client.cases.get_endpoints(case_id, filter_params)      # Get case endpoints
client.cases.get_tasks(case_id, filter_params)          # Get case tasks
client.cases.get_users(case_id, filter_params)          # Get case users

# Case Operations
client.cases.remove_endpoints(case_id, filter_params)   # Remove endpoints
client.cases.remove_task_assignment(case_id, task_assignment_id)  # Remove task
client.cases.import_task_assignments(case_id, task_assignment_ids)  # Import tasks

# Notes
client.cases.add_note(case_id, note)                    # Add note
client.cases.update_note(case_id, note_id, note)        # Update note
client.cases.delete_note(case_id, note_id)              # Delete note

# Export
client.cases.export_notes(case_id)                      # Export notes
client.cases.export_cases(filter_params)                # Export cases
client.cases.export_endpoints(case_id, filter_params)   # Export endpoints
client.cases.export_activities(case_id, filter_params)  # Export activities
```

### **🖥️ Assets**

```python
# Asset Information
client.assets.list(filter_params)                       # List assets
client.assets.get(asset_id)                             # Get asset details
client.assets.get_tasks(asset_id, filter_params)        # Get asset tasks

# Asset Control
client.assets.isolate(endpoint_ids, organization_ids)   # Isolate assets
client.assets.unisolate(endpoint_ids, organization_ids) # Remove isolation
client.assets.reboot(endpoint_ids, organization_ids)    # Reboot assets
client.assets.shutdown(endpoint_ids, organization_ids)  # Shutdown assets

# Asset Management
client.assets.add_tags(endpoint_ids, tags, organization_ids)     # Add tags
client.assets.remove_tags(endpoint_ids, tags, organization_ids)  # Remove tags
client.assets.uninstall(endpoint_ids, purge_data, organization_ids)  # Uninstall
client.assets.retrieve_logs(endpoint_ids, organization_ids)     # Retrieve logs
client.assets.version_update(endpoint_ids, organization_ids)    # Update version
```

### **📊 Tasks**

```python
client.tasks.list(filter_params, organization_ids)      # List tasks
client.tasks.get(task_id)                               # Get task details
client.tasks.get_assignments(task_id)                   # Get task assignments
client.tasks.cancel(task_id)                            # Cancel task
client.tasks.delete(task_id)                            # Delete task
client.tasks.cancel_assignment(assignment_id)           # Cancel assignment
client.tasks.delete_assignment(assignment_id)           # Delete assignment
```

### **🔍 Triage**

```python
# Rules
client.triage.list_rules(filter_params, organization_ids)  # List rules
client.triage.create_rule(rule_data)                    # Create rule
client.triage.get_rule(rule_id)                         # Get rule
client.triage.get_rule_by_id(rule_id)                   # Get rule (alias)
client.triage.update_rule(rule_id, data)                # Update rule
client.triage.delete_rule(rule_id)                      # Delete rule
client.triage.validate_rule(rule_content, engine)       # Validate rule

# Tags & Tasks
client.triage.list_tags(organization_id)                # List tags
client.triage.create_tag(tag_data)                      # Create tag
client.triage.delete_tag(tag_id)                        # Delete tag
client.triage.assign_task(task_data)                    # Assign task
```

### **📋 Policies**

```python
# Policy Management
client.policies.list(filter_params, organization_ids)   # List policies
client.policies.get(policy_id)                          # Get policy
client.policies.create(policy_data)                     # Create policy
client.policies.update(policy_id, update_data)          # Update policy
client.policies.delete(policy_id)                       # Delete policy
client.policies.activate(policy_id)                     # Activate policy
client.policies.deactivate(policy_id)                   # Deactivate policy

# Policy Operations
client.policies.get_assignments(policy_id)              # Get assignments
client.policies.get_executions(policy_id)               # Get executions
client.policies.assign(assignment_data)                 # Assign policy
client.policies.unassign(policy_id, endpoint_ids)       # Unassign policy
client.policies.execute(policy_id, endpoint_ids)        # Execute policy
client.policies.get_match_stats(filter_params, organization_ids)  # Get stats
client.policies.update_priorities(policy_ids, organization_ids)   # Update priorities
```

### **🔐 Authentication**

```python
client.authentication.login(credentials)                # Login with credentials
client.authentication.check_status()                    # Check auth status
```

### **🏢 Organizations**

```python
# Organization Management
client.organizations.list(page, page_size, sort_by, order)  # List organizations
client.organizations.create(org_data)                   # Create organization
client.organizations.get(org_id)                        # Get organization
client.organizations.update(org_id, data)               # Update organization
client.organizations.delete(org_id)                     # Delete organization
client.organizations.check_name(name)                   # Check name availability

# User Management
client.organizations.get_users(org_id, page, page_size) # Get org users
client.organizations.add_user(org_id, user_data)        # Add user
client.organizations.assign_users(org_id, user_ids)     # Assign users
client.organizations.remove_user(org_id, user_id)       # Remove user

# Settings & Configuration
client.organizations.update_settings(org_id, settings)  # Update settings
client.organizations.get_shareable_deployment_info(token)  # Get deployment info
client.organizations.update_shareable_deployment_settings(org_id, status)  # Update deployment
client.organizations.update_deployment_token(org_id, token)  # Update token

# Tags
client.organizations.add_tags(org_id, tags)             # Add tags
client.organizations.delete_tags(org_id, tags)          # Delete tags
client.organizations.remove_tags(org_id, tags)          # Remove tags (alias)
```

### **👥 Users**

```python
client.user_management.list_users()                     # List users
client.user_management.get_user(user_id)                # Get user details
client.user_management.create_api_user(user_data)       # Create API user
```

### **📊 Audit**

```python
client.audit.list_logs(filter_params, organization_ids) # List audit logs
client.audit.get_log(log_id)                            # Get audit log
client.audit.export_logs(filter_params, format, organization_ids)  # Export logs
client.audit.get_summary(org_id, start_date, end_date)  # Get summary
client.audit.get_user_activity(org_id, start_date, end_date, user_id)  # Get activity
client.audit.get_system_events(org_id, start_date, end_date, severity)  # Get events
client.audit.get_retention_policy(org_id)               # Get retention policy
```

### **📈 Baseline**

```python
# Baseline Management
client.baseline.list(filter_params, organization_ids)   # List baselines
client.baseline.create(request)                         # Create baseline
client.baseline.get(baseline_id)                        # Get baseline
client.baseline.update(baseline_id, request)            # Update baseline
client.baseline.delete(baseline_id)                     # Delete baseline
client.baseline.refresh(baseline_id)                    # Refresh baseline

# Comparisons
client.baseline.get_comparisons(baseline_id)            # Get comparisons
client.baseline.get_comparison(comparison_id)           # Get comparison
client.baseline.compare(request)                        # Run comparison
client.baseline.get_comparison_report(baseline_id, task_id)  # Get report

# Profiles & Schedules
client.baseline.list_profiles(organization_ids)         # List profiles
client.baseline.get_profile(profile_id)                 # Get profile
client.baseline.create_profile(request)                 # Create profile
client.baseline.update_profile(profile_id, request)     # Update profile
client.baseline.delete_profile(profile_id)              # Delete profile
client.baseline.get_schedules(baseline_id, organization_ids)  # Get schedules
client.baseline.create_schedule(baseline_id, schedule_data)  # Create schedule
client.baseline.delete_schedule(schedule_id)            # Delete schedule

# Advanced Operations
client.baseline.acquire(baseline_data)                  # Acquire baseline
client.baseline.acquire_by_filter(filter_data, case_id) # Acquire by filter
client.baseline.compare_by_endpoint(endpoint_id, task_ids)  # Compare by endpoint
```

### **📚 Evidence**

```python
# Case Evidence (Read-only)
client.evidence.get_case_evidence_ppc(endpoint_id, task_id)  # Get PPC
client.evidence.get_case_evidence_report_file_info(endpoint_id, task_id)  # Get file info
client.evidence.get_case_evidence_report(endpoint_id, task_id)  # Get report

# Repository Operations (delegates to evidences API)
client.evidence.list_repositories()                     # List repositories
```

### **📚 Evidences (Repository Management)**

```python
# Repository Management
client.evidences.list_repositories()                    # List all repositories

# SMB Repositories
client.evidences.create_smb_repository(request)         # Create SMB
client.evidences.update_smb_repository(repo_id, request)  # Update SMB

# SFTP Repositories
client.evidences.create_sftp_repository(request)        # Create SFTP
client.evidences.update_sftp_repository(repo_id, request)  # Update SFTP

# FTPS Repositories
client.evidences.create_ftps_repository(request)        # Create FTPS
client.evidences.update_ftps_repository(repo_id, request)  # Update FTPS
client.evidences.validate_ftps_repository(request)      # Validate FTPS

# Azure Storage Repositories
client.evidences.create_azure_repository(request)       # Create Azure
client.evidences.update_azure_repository(repo_id, request)  # Update Azure
client.evidences.validate_azure_repository(request)     # Validate Azure

# Amazon S3 Repositories
client.evidences.create_s3_repository(request)          # Create S3
client.evidences.update_s3_repository(repo_id, request) # Update S3
client.evidences.validate_s3_repository(request)        # Validate S3

# Repository Operations
client.evidences.delete_repository(repo_id)             # Delete repository
client.evidences.validate_repository(request)           # Validate repository
client.evidences.get_repository_volumes(repo_id)        # Get volumes
```

### **🏷️ Auto Asset Tags**

```python
client.auto_asset_tags.list(filter_params)              # List auto tags
client.auto_asset_tags.create(request)                  # Create auto tag
client.auto_asset_tags.get(tag_id)                      # Get auto tag
client.auto_asset_tags.update(tag_id, request)          # Update auto tag
client.auto_asset_tags.delete(tag_id)                   # Delete auto tag
client.auto_asset_tags.start_tagging(request)           # Start tagging
```

### **📡 Event Subscription**

```python
client.event_subscription.list(filter_params)           # List subscriptions
client.event_subscription.create(request)               # Create subscription
client.event_subscription.get(subscription_id)          # Get subscription
client.event_subscription.update(subscription_id, request)  # Update subscription
client.event_subscription.delete(subscription_id)       # Delete subscription
```

### **💬 Interact**

```python
client.interact.assign_shell_task(request)              # Assign shell task
client.interact.get_shell_task_response(task_id)        # Get shell response
```

### **⚙️ Params**

```python
client.params.get_drone_analyzers()                     # Get drone analyzers
client.params.get_acquisition_artifacts()               # Get acquisition artifacts
client.params.get_acquisition_evidences()               # Get acquisition evidences
client.params.get_e_discovery_patterns()                # Get e-discovery patterns
```

### **⚙️ Settings**

```python
client.settings.get_banner_settings()                   # Get banner settings
client.settings.update_banner_settings(request)         # Update banner settings
```

### **🏷️ Endpoints**

```python
client.endpoints.get_tags(filter_params)                # Get endpoint tags
```

### **🔗 Webhooks**

```python
client.webhooks.trigger_get(slug, token)                # Trigger GET webhook
client.webhooks.trigger_post(slug, token, payload)      # Trigger POST webhook
client.webhooks.get_task_details(slug, token, task_id)  # Get task details
```

## 🔧 Configuration Options

### **Environment Variables**

```bash
export AIR_HOST="https://your-air-instance.com"
export AIR_API_TOKEN="your-api-token"
export AIR_ORGANIZATION_ID="0"
export AIR_VERIFY_SSL="true"
export AIR_TIMEOUT="30"
```

### **Configuration File (config.json)**

```json
{
	"host": "https://your-air-instance.com",
	"api_token": "your-api-token",
	"organization_id": 0,
	"verify_ssl": true,
	"timeout": 30
}
```

### **Programmatic Configuration**

```python
from binalyze_air import AIRClient, AIRConfig

# Using config object
config = AIRConfig(
    host="https://your-air-instance.com",
    api_token="your-api-token",
    organization_id=0,
    verify_ssl=False,
    timeout=60
)
client = AIRClient(config=config)

# Direct initialization
client = AIRClient(
    host="https://your-air-instance.com",
    api_token="your-api-token",
    organization_id=0
)

# From environment
client = AIRClient.from_environment()

# From config file
client = AIRClient.from_config_file("config.json")
```

## 🏗️ Architecture & Design

### **CQRS Pattern**

Clean separation of read and write operations:

```python
# Queries (Read operations)
assets = client.assets.list()
asset = client.assets.get("asset-id")
cases = client.cases.list(filter_params)

# Commands (Write operations)
client.assets.isolate(["endpoint-id"])
client.cases.create(case_data)
client.policies.execute("policy-id", ["endpoint-id"])
```

### **Type Safety with Pydantic V2**

```python
from binalyze_air.models.cases import CreateCaseRequest
from binalyze_air.models.assets import AssetFilter

# Type-safe request objects
case_request = CreateCaseRequest(
    name="Investigation",
    description="Security incident",
    visibility="public-to-organization"
)
case = client.cases.create(case_request)

# Type-safe filtering
asset_filter = AssetFilter(
    organization_ids=[0],
    online_status=["online"],
    tags=["production"]
)
assets = client.assets.list(asset_filter)
```

### **Comprehensive Error Handling**

```python
from binalyze_air.exceptions import (
    AIRAPIError,
    AuthenticationError,
    AuthorizationError,
    ValidationError
)

try:
    case = client.cases.create(case_data)
except AuthenticationError:
    print("Invalid API token")
except AuthorizationError:
    print("Insufficient permissions")
except ValidationError as e:
    print(f"Validation failed: {e}")
except AIRAPIError as e:
    print(f"API error: {e}")
```

## 🧪 Testing & Quality

### **Comprehensive Test Suite**

- **Real system validation** with actual AIR instance
- **100% field mapping accuracy** verification
- **Error scenario testing** for robust error handling
- **Cross-platform compatibility** testing

### **Running Tests**

```bash
# Run individual SDK tests
python tests_sdk/001_acquisitions_01_get_acquisition_profiles_REAL_test.py
python tests_sdk/007_cases_08_get_cases_REAL_test.py
python tests_sdk/013_policies_03_get_policies_REAL_test.py

# Run API tests
python tests_api/001_acquisitions_01_get_acquisition_profiles_test.py
python tests_api/007_cases_08_get_cases_test.py

# Run test suites
python run_sdk_tests.ps1    # PowerShell
python run_all_tests.ps1    # PowerShell
```

### **Quality Metrics**

- ✅ **Production Ready**: All core endpoints tested
- ✅ **Cross-Platform**: Windows, Linux, macOS compatible
- ✅ **ASCII Output**: Universal compatibility
- ✅ **Real Data Testing**: Validated with live system
- ✅ **Dynamic Discovery**: No hardcoded test values

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in minutes
- **[SDK Documentation](SDK_DOCUMENTATION.md)** - Complete API reference
- **[Test Results](tests_sdk/)** - SDK test suite
- **[API Tests](tests_api/)** - API validation tests

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/binalyze/air-python-sdk/issues)
- **Documentation**: [GitHub Wiki](https://github.com/binalyze/air-python-sdk/wiki)
- **Email**: support@binalyze.com

## 🎉 Acknowledgments

- **Binalyze Team** for the incredible AIR platform
- **Python Community** for excellent libraries and tools
- **Contributors** who helped build this comprehensive SDK

---

**🏆 PRODUCTION READY SDK**

_A comprehensive, production-ready Python SDK for the Binalyze AIR cybersecurity platform. From asset management to evidence acquisition, from policy enforcement to triage automation - everything is at your fingertips._
