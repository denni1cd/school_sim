# Project Specification

This file is the project specification. Complete all sections before runtime. Use full terms. Do not use abbreviations.

```yaml
---
project:
  title: "<Project Name>"
  summary: "<One or two sentences>"
  author: "<Author or Organization>"
  date: "<YYYY-MM-DD>"
---
```

## Background
<Provide context and drivers.>

## Goals
- <Goal 1>
- <Goal 2>
- <Goal 3>

```yaml
---
requirements:
  functional:
    - id: "Functional Requirement 1"
      description: "<Description>"
    - id: "Functional Requirement 2"
      description: "<Description>"
  non_functional:
    - id: "Non-Functional Requirement 1"
      description: "<Description>"
    - id: "Non-Functional Requirement 2"
      description: "<Description>"
constraints:
  - "<Binding rule>"
  - "<Binding rule>"
assumptions:
  - "<Assumption>"
  - "<Assumption>"
tech_stack:
  runtime:
    language: "<Language and version>"
    framework: "<Framework and version>"
  storage:
    database: "<Database and version>"
    orm: "<ORM and version>"
  services:
    auth: "<Authentication approach and library>"
    messaging: "<Queue or stream technology if used>"
  frontend:
    web: "<Web framework and version or NONE>"
    mobile: "<Mobile approach or NONE>"
  deployment:
    platform: "<Platform>"
    ci_cd: "<Pipeline requirements>"
  logging_observability:
    logging: "<Stack>"
    auditing: "<Approach>"
milestones:
  - name: "<Milestone 1 name>"
    target_date: "<YYYY-MM-DD or phase name>"
    scope: "<Scope>"
  - name: "<Milestone 2 name>"
    target_date: "<YYYY-MM-DD or phase name>"
    scope: "<Scope>"
acceptance_criteria:
  - "<Criterion 1>"
  - "<Criterion 2>"
---
```

## Use Cases
- <Use Case 1>
- <Use Case 2>

## Additional Notes
<Notes>
