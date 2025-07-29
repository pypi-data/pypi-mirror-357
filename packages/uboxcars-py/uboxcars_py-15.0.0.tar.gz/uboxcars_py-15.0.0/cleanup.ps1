# cleanup_build.ps1

Write-Host " Removing old build artifacts..."
Remove-Item -Recurse -Force build, dist, *.egg-info -ErrorAction SilentlyContinue

Write-Host " Regenerating poetry.lock..."
poetry lock

Write-Host " Installing dependencies with Poetry..."
poetry install

Write-Host " Building with Cargo..."
cargo build

Write-Host " Building with Poetry..."
poetry build

Write-Host " Building native extension with maturin..."
poetry run maturin build

Write-Host " Running Makefile (if it exists)..."
if (Test-Path ".\Makefile") {
    bash -c "make"
} else {
    Write-Host " No Makefile found."
}

Write-Host " Uploading to PyPI with Twine..."
python -m twine upload dist/*
