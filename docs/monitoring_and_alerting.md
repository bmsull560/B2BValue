# Monitoring and Alerting in B2BValue

## Overview
B2BValue includes built-in monitoring and alerting hooks for all critical memory and agent operations. This ensures that operational issues, security events, and unexpected failures are tracked and can be surfaced for human or automated intervention.

## Logging Structure
- **Standard Logs:** All major operations are logged using Python's standard logging system. These logs include info, warning, and error messages for all memory and agent activities.
- **Critical Log File:** All errors and critical events are also logged to a dedicated file at `logs/critical.log`. This file is designed for integration with external monitoring/alerting systems (e.g., log shippers, SIEM, or custom scripts).

## What Gets Logged?
- **Memory Operations:**
  - Store, retrieve, search, and delete actions for all memory tiers.
  - Errors and exceptions during memory operations.
- **Agent Operations:**
  - Agent execution start, success, and failure.
  - Workflow lifecycle events.
- **Access Control:**
  - Permission denials and access violations.
- **Integrity Checks:**
  - Checksum mismatches and possible tampering.

## Example: Critical Log Entry
```text
2025-06-12 10:30:00,123 ERROR STORE ERROR: Failed to store entity 1234 in tier EPISODIC: [Exception details]
2025-06-12 10:30:00,124 CRITICAL CRITICAL STORE ERROR: [Exception details]
```

## Alerting Integration
- **Manual:** Regularly review `logs/critical.log` for issues.
- **Automated:** Integrate with tools like `logwatch`, `filebeat`, or cloud log monitoring to trigger alerts on new critical log entries.

## Troubleshooting
- Review `logs/critical.log` for errors and critical events.
- Check standard logs for detailed operation traces.
- Ensure log file permissions allow the application to write logs.

## Extending Monitoring
- Add custom log handlers to integrate with Slack, email, or incident response tools.
- Expand logging in agents for business-specific events.
