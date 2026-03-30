GPO Export — HawkinsOps Security Baseline
==========================================

Contents:
  GPO-export.xml — Full Group Policy Object export (sanitized)

What the GPO contains:
  - 22 Advanced Audit Policy subcategories set to Success + Failure
  - CommandLine capture enabled (ProcessCreationIncludeCmdLine_Enabled = 1)
  - Security log max size set to 1 GB (1,048,576 KB)
  - Log retention: Overwrite as needed

How to import:
  1. Open Group Policy Management Console (gpmc.msc)
  2. Right-click the target OU > "Import Settings..."
  3. Browse to GPO-export.xml
  4. Review the settings before applying

  Alternatively, use PowerShell:
    Import-GPO -BackupGpoName "HawkinsOps Security Baseline" -TargetName "Your GPO Name" -Path ".\gpo\"

Sanitization notes:
  - Domain names replaced with SIGNALFOUNDRY.LOCAL
  - Computer names replaced with <HOST>
  - SIDs replaced with generic placeholders
  - No credentials or secrets present in export
