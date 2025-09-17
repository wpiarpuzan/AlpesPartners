<#
PowerShell helper to deploy the project to Heroku using the Container Registry (Docker).
This script DOES NOT include any credentials. You must be logged into the Heroku CLI before running.
It will:
 - check for heroku CLI
 - login to container registry
 - create app (if it doesn't exist)
 - provision Postgres add-on
 - set required config vars
 - build and push the Docker image to Heroku
 - release the image and tail logs

Run this script from the repo root in PowerShell: 
  ./scripts/deploy_heroku.ps1 -AppName alpespartners
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$AppName
)

function Check-Command($cmd) {
    $p = Get-Command $cmd -ErrorAction SilentlyContinue
    if (-not $p) { Write-Error "Required command '$cmd' not found in PATH. Install it and retry."; exit 1 }
}

Check-Command heroku
Check-Command docker

Write-Host "Please ensure you're logged into Heroku (heroku login) in this shell."
Write-Host "If not, run: heroku login" -ForegroundColor Yellow

# Login to Heroku container registry
Write-Host "Logging in to Heroku container registry..."
heroku container:login

# Create app (ignore failure if already exists)
Write-Host "Creating Heroku app (if it doesn't exist): $AppName"
try { heroku apps:create $AppName } catch { Write-Host "App may already exist, continuing..." }
# Verify app exists now (exit with clear instructions if creation failed due to account verification)
Write-Host "Verifying Heroku app exists: $AppName"
& heroku apps:info -a $AppName 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Error "Heroku app '$AppName' was not found or couldn't be created."
  Write-Error "Common causes: your account needs verification (add payment info) or you lack permissions to create apps."
  Write-Error "To proceed, either: (1) verify your account at https://heroku.com/verify, or (2) create the app manually with: heroku apps:create $AppName"
  exit 1
}

# Provision Postgres
Write-Host "Provisioning Heroku Postgres (hobby-basic). This will take a moment..."
try { heroku addons:create heroku-postgresql:hobby-basic -a $AppName } catch { Write-Host "Addon creation may have failed or already exists, continuing..." }

# Set config vars for DB_OUTBOX demo
Write-Host "Setting config vars MESSAGE_BUS=DB_OUTBOX and MIGRATE_ON_START=true"
heroku config:set MESSAGE_BUS=DB_OUTBOX MIGRATE_ON_START=true -a $AppName

# Build Docker image for Heroku
Write-Host "Building Docker image and pushing to Heroku Container Registry..."
# Tag name required by Heroku registry
$herokuImage = "registry.heroku.com/$AppName/web"
# Choose a Dockerfile to use. Prefer root 'Dockerfile', then 'alpespartners.Dockerfile', then 'Dockerfile.publisher'.
if (Test-Path "Dockerfile") {
  $dockerfile = "Dockerfile"
} elseif (Test-Path "alpespartners.Dockerfile") {
  $dockerfile = "alpespartners.Dockerfile"
} elseif (Test-Path "Dockerfile.publisher") {
  $dockerfile = "Dockerfile.publisher"
} else {
  Write-Error "No Dockerfile found in repo root. Create a 'Dockerfile' or add one of: 'alpespartners.Dockerfile' or 'Dockerfile.publisher'."
  exit 1
}
Write-Host "Using Dockerfile: $dockerfile"
docker build -f $dockerfile -t $herokuImage .

# Push and release
heroku container:push web -a $AppName
heroku container:release web -a $AppName

# Scale web dyno
heroku ps:scale web=1 -a $AppName

# Tail logs briefly to observe startup
Write-Host "Tailing Heroku logs (press Ctrl+C to stop)..."
heroku logs --tail -a $AppName

Write-Host "Deployment script finished. If migrations didn't run automatically, you can run them via:"
Write-Host ('heroku run python -a {0} -c "from alpespartners.config.migrations import run_startup_migrations; run_startup_migrations()"' -f $AppName)
Write-Host ("Then run Newman locally against: https://{0}.herokuapp.com (use --delay-request 4000 for reliability)" -f $AppName)
