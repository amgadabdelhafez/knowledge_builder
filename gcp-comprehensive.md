# Google Cloud Platform (GCP) Complete Reference

## Table of Contents
1. [Infrastructure and Core Services](#infrastructure-and-core-services)
2. [Storage and Databases](#storage-and-databases)
3. [Networking](#networking)
4. [Security and Identity](#security-and-identity)
5. [Data and Analytics](#data-and-analytics)
6. [AI and Machine Learning](#ai-and-machine-learning)
7. [HPC and Workflow Management](#hpc-and-workflow-management)
8. [Developer Tools and Services](#developer-tools-and-services)
9. [Management and Operations](#management-and-operations)
10. [Pricing and Billing](#pricing-and-billing)

## Infrastructure and Core Services
### Compute Engine
- Machine Types
  - General-purpose (E2, N1, N2, N2D)
  - Compute-optimized (C2, C2D)
  - Memory-optimized (M1, M2)
  - Accelerator-optimized (A2)
- Instance Features
  - Custom Machine Types
  - Preemptible VMs
  - Spot VMs
  - Sole-tenant Nodes
  - Shielded VMs
  - Confidential VMs
- Instance Groups
  - Managed Instance Groups
  - Unmanaged Instance Groups
  - Regional Instance Groups
  - Zonal Instance Groups
- Instance Templates
- OS Images
  - Public Images
  - Custom Images
  - Container-Optimized OS
  - Windows Server Images
- Disk Options
  - Persistent Disks
  - Local SSDs
  - Regional Disks
  - Multi-Regional Disks

### Google Kubernetes Engine (GKE)
- Cluster Types
  - Standard Clusters
  - Autopilot Clusters
  - Private Clusters
- Node Configuration
  - Node Pools
  - Node Images
  - Node Taints
  - Node Labels
- Workload Management
  - Deployments
  - StatefulSets
  - DaemonSets
  - Jobs/CronJobs
- Cluster Features
  - Auto-scaling
  - Auto-upgrading
  - Auto-repair
  - Binary Authorization
  - Workload Identity
- Networking
  - Container-native Load Balancing
  - Ingress Controllers
  - Network Policies
  - Service Mesh

### Cloud Run
- Service Configuration
  - Container Instances
  - Revision Management
  - Traffic Splitting
- Autoscaling
  - Concurrent Requests
  - CPU Utilization
  - Memory Utilization
- Networking
  - Custom Domains
  - Cloud CDN Integration
  - VPC Connector
- Security
  - IAM Integration
  - Cloud KMS Integration
  - Binary Authorization

### App Engine
- Environments
  - Standard Environment
  - Flexible Environment
- Runtime Support
  - Python
  - Java
  - Node.js
  - Go
  - PHP
  - Ruby
- Features
  - Traffic Splitting
  - Version Management
  - Custom Domains
  - SSL Certificates
- Services
  - Default Service
  - Custom Services
  - Service Scaling
  - Service Versions

## Storage and Databases
### Cloud Storage
- Storage Classes
  - Standard Storage
  - Nearline Storage
  - Coldline Storage
  - Archive Storage
- Bucket Features
  - Location Type
  - Storage Type
  - Access Control
  - Lifecycle Management
- Object Features
  - Object Versioning
  - Object Lifecycle
  - Object Hold
  - Object Retention
- Data Transfer
  - Transfer Service
  - Transfer Appliance
  - Storage Transfer Service
  - gsutil

### Cloud SQL
- Database Engines
  - MySQL
  - PostgreSQL
  - SQL Server
- Features
  - High Availability
  - Read Replicas
  - Automatic Backups
  - Point-in-time Recovery
- Connectivity
  - Private IP
  - Cloud SQL Proxy
  - SSL/TLS
- Operations
  - Maintenance Windows
  - Instance Operations
  - Backup Operations
  - Import/Export Operations

### Cloud Spanner
- Instance Configuration
  - Node Count
  - Processing Units
  - Regional/Multi-Regional
- Database Features
  - Schemas
  - Indexes
  - Interleaved Tables
  - Foreign Keys
- Operations
  - Backups
  - Restores
  - Import/Export
  - Mutations
- Query Features
  - SQL Support
  - Query Optimization
  - Query Planning
  - Query Statistics

### Cloud Bigtable
- Instance Types
  - Production
  - Development
- Cluster Management
  - Auto-scaling
  - Replication
  - Node Count
- Tables
  - Column Families
  - Row Keys
  - Schema Design
- Operations
  - Backup/Restore
  - Import/Export
  - Monitoring
  - Performance Optimization

## Networking
### Virtual Private Cloud (VPC)
- Network Components
  - Subnets
  - Routes
  - Firewall Rules
  - VPC Peering
- IP Addressing
  - Internal IP Ranges
  - External IP Addresses
  - Alias IP Ranges
  - Secondary IP Ranges
- Connectivity Options
  - Cloud VPN
  - Cloud Interconnect
  - Direct Peering
  - Carrier Peering
- VPC Features
  - Shared VPC
  - VPC Service Controls
  - VPC Flow Logs
  - Network Tags

### Load Balancing
- Load Balancer Types
  - HTTP(S) Load Balancing
  - TCP/SSL Proxy Load Balancing
  - Network Load Balancing
  - Internal Load Balancing
- Features
  - SSL Certificates
  - URL Maps
  - Backend Services
  - Health Checks
- Global Load Balancing
  - Cross-Region Load Balancing
  - Multi-Region Failover
  - Anycast IP Addresses
- Regional Load Balancing
  - Internal TCP/UDP
  - Internal HTTP(S)
  - Network Load Balancing

### Cloud CDN
- Cache Features
  - Cache Modes
  - Cache Keys
  - Cache Invalidation
  - Cache Bypass
- Security
  - Signed URLs
  - Signed Cookie Authentication
  - Token Authentication
- Operations
  - Cache Hit Ratio
  - Cache Statistics
  - Origin Shield
  - Custom Domains

### Cloud DNS
- Zone Types
  - Public Zones
  - Private Zones
  - Forwarding Zones
- Record Types
  - A Records
  - AAAA Records
  - CNAME Records
  - MX Records
  - TXT Records
- Features
  - DNSSEC
  - Cloud DNS Policies
  - DNS Peering
  - Managed Zones

## Security and Identity
### Identity and Access Management (IAM)
- Identity Types
  - User Accounts
  - Service Accounts
  - Google Groups
  - Google Workspace Domains
- Role Types
  - Primitive Roles
  - Predefined Roles
  - Custom Roles
- Policy Management
  - IAM Policies
  - Organization Policies
  - Resource Hierarchy
- Conditional Access
  - IP-based Access
  - Device-based Access
  - Context-aware Access
  - Resource-based Access

### Security Command Center
- Security Sources
  - Security Health Analytics
  - Event Threat Detection
  - Container Threat Detection
  - Web Security Scanner
- Features
  - Asset Discovery
  - Vulnerability Scanning
  - Security Findings
  - Risk Analysis
- Operations
  - Finding Management
  - Security Notifications
  - Compliance Reports
  - Security Metrics

### Cloud KMS
- Key Management
  - Key Creation
  - Key Rotation
  - Key Destruction
  - Key Import
- Key Types
  - Symmetric Keys
  - Asymmetric Keys
  - HSM Keys
- Operations
  - Encryption/Decryption
  - Signing/Verification
  - Key Versioning
  - Key Usage Analytics

## Data and Analytics
### BigQuery
- Data Organization
  - Datasets
  - Tables
  - Views
  - Materialized Views
- Table Types
  - Native Tables
  - External Tables
  - Partitioned Tables
  - Clustered Tables
- Query Features
  - Standard SQL
  - Legacy SQL
  - Query Planning
  - Query Caching
- Performance Features
  - Slot Capacity
  - Reservation Model
  - Capacity Commitments
  - BI Engine
- Data Movement
  - Load Jobs
  - Export Jobs
  - Transfer Service
  - Data Share
- Security
  - Column-level Security
  - Row-level Security
  - Data Masking
  - Authorized Views

### Dataflow
- Pipeline Types
  - Batch Processing
  - Stream Processing
  - Flex Templates
- Pipeline Features
  - Auto-scaling
  - Monitoring
  - Data Windowing
  - Triggers
- Operations
  - Job Launch
  - Job Monitoring
  - Job Updates
  - Error Handling
- Integration
  - Source Connectors
  - Sink Connectors
  - Custom Functions
  - Pipeline Templates

### Dataproc
- Cluster Types
  - Standard Clusters
  - Single Node Clusters
  - High Availability Clusters
- Cluster Features
  - Auto-scaling
  - Preemptible Workers
  - Custom Images
  - Initialization Actions
- Job Types
  - Hadoop Jobs
  - Spark Jobs
  - Hive Jobs
  - Pig Jobs
- Operations
  - Workflow Templates
  - Job Scheduling
  - Monitoring
  - Logging

## AI and Machine Learning
### Vertex AI
- Training
  - AutoML Training
  - Custom Training
  - Hyperparameter Tuning
  - Distributed Training
- Model Management
  - Model Registry
  - Model Versioning
  - Model Deployment
  - Model Monitoring
- Feature Store
  - Feature Definition
  - Feature Serving
  - Feature Monitoring
  - Feature Discovery
- MLOps
  - Pipelines
  - Experiments
  - Metadata
  - Artifacts
- Endpoints
  - Online Prediction
  - Batch Prediction
  - Model Serving
  - Traffic Splitting

### Specialized AI Services
- Vision AI
  - Object Detection
  - OCR
  - Label Detection
  - Face Detection
- Natural Language
  - Entity Analysis
  - Sentiment Analysis
  - Content Classification
  - Syntax Analysis
- Speech AI
  - Speech-to-Text
  - Text-to-Speech
  - Speaker Recognition
  - Audio Transcription
- Translation AI
  - Language Detection
  - Translation
  - Glossary Management
  - AutoML Translation

## HPC and Workflow Management
### HPC Infrastructure
- Compute Resources
  - HPC-optimized Instances
  - GPU Instances
  - High Memory Instances
  - Local SSD Optimization
- Network Resources
  - High-throughput Networking
  - InfiniBand
  - Placement Groups
  - Low-latency Connections
- Storage Resources
  - Parallel File Systems
  - High IOPS Storage
  - Storage Classes
  - Cache Tiering

### Job Scheduling
- Slurm Integration
  - Slurm Commands
    - srun
    - sbatch
    - squeue
    - scancel
    - scontrol
  - Slurm Configuration
    - slurm.conf
    - cgroup.conf
    - gres.conf
  - Accounting
    - sacct
    - sreport
    - sshare
- Queue Management
  - Queue Types
    - FIFO Queues
    - Priority Queues
    - Fair-share Queues
  - Queue Policies
    - Resource Limits
    - Time Limits
    - User Limits
  - Preemption
    - Job Preemption
    - Resource Preemption
    - Priority Preemption

### Workflow Management
- Cloud Composer
  - DAG Management
    - DAG Definition
    - DAG Scheduling
    - DAG Dependencies
  - Operators
    - BigQueryOperator
    - DataflowOperator
    - GCSOperator
    - KubernetesPodOperator
  - Workflow Features
    - Task Dependencies
    - Branching
    - XCom
    - Sensors
- Cloud Life Sciences
  - Pipeline Components
    - Actions
    - Resources
    - Environment
  - Operations
    - Monitoring
    - Logging
    - Error Handling

### Batch Processing
- Cloud Batch
  - Job Configuration
    - Task Groups
    - Task Templates
    - Resource Allocation
  - Execution
    - Parallel Processing
    - Sequential Processing
    - Job Arrays
  - Management
    - Job Monitoring
    - Error Handling
    - Resource Management

## Developer Tools and Services
### Cloud Build
- Build Configuration
  - cloudbuild.yaml
  - Dockerfile
  - Build Steps
  - Build Triggers
- Build Features
  - Docker Support
  - Language Support
  - Testing Integration
  - Artifact Creation
- Integration
  - Source Repositories
  - Container Registry
  - Artifact Registry
  - Cloud Storage

### Cloud Source Repositories
- Repository Management
  - Git Operations
  - Code Review
  - Branch Protection
  - Merged History
- Integration
  - Cloud Build
  - Cloud Pub/Sub
  - IAM
  - Logging

### Container Registry/Artifact Registry
- Container Management
  - Image Storage
  - Image Scanning
  - Image Signing
  - Image Lifecycle
- Package Management
  - Maven
  - npm
  - Python Packages
  - Docker Images
- Security
  - Vulnerability Scanning
  - Access Control
  - SHA Validation
  - Tag Immutability

## Management and Operations
### Cloud Monitoring
- Metrics
  - System Metrics
  - Custom Metrics
  - Log-based Metrics
  - Uptime Checks
- Dashboards
  - Predefined Dashboards
  - Custom Dashboards
  - Chart Types
  - Dashboard Sharing
- Alerting
  - Alert Policies
  - Notification Channels
  - Alert Conditions
  - Alert Documentation

### Cloud Logging
- Log Types
  - Platform Logs
  - Application Logs
  - Security Logs
  - Audit Logs
- Log Management
  - Log Router
  - Log Sinks
  - Log Exclusions
  - Log Retention
- Log Analysis
  - Log Explorer
  - Log Analytics
  - Log Search
  - Log Metrics

## Pricing and Billing
### Billing Models
- On-demand Pricing
  - Per-second Billing
  - Resource-based Pricing
  - Network Pricing
  - Storage Pricing
- Committed Use Discounts
  - 1-year Commitment
  - 3-year Commitment
  - Resource CUDs
  - Spend-based CUDs
- Sustained Use Discounts
  - Automatic Discounts
  - Usage Calculation
  - Eligible Services
  - Discount Tiers
- Special Instance Pricing
  - Preemptible VMs
  - Spot VMs
  - Sole-tenant Nodes
  - Custom Machine Types

### Billing Management
- Billing Accounts
  - Master Billing Account
  - Sub Accounts
  - Billing Permissions
  - Payment Methods
- Budgets and Alerts
  - Budget Creation
  - Alert Thresholds
  - Budget Actions
  - Notification Channels
- Cost Management
  - Cost Tables
  - Cost Reports
  - Cost Allocation
  - Resource Labels
- Billing Export
  - BigQuery Export
  - Cloud Storage Export
  - File Export
  - Custom Export

### Cost Optimization
- Resource Optimization
  - Right-sizing
  - Automated Recommendations
  - Idle Resource Detection
  - Resource Cleanup
- Pricing Tools
  - Pricing Calculator
  - Total Cost of Ownership
  - Committed Use Calculator
  - Custom Quote Builder
- Cost Controls
  - Quotas
  - Limits
  - Constraints
  - Budget Controls
