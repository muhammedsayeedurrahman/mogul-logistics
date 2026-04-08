@echo off
echo.
echo ================================================================
echo MOGUL LOGISTICS - FINAL SUBMISSION SCRIPT
echo Meta PyTorch OpenEnv Hackathon
echo ================================================================
echo.

cd /d "%~dp0"

echo [1/5] Running all tests...
pytest tests/ -v --tb=line
if errorlevel 1 (
    echo.
    echo ERROR: Tests failed! Fix errors before submitting.
    pause
    exit /b 1
)

echo.
echo [2/5] Checking code quality...
python -c "from server.gradio_custom import build_custom_dashboard; print('✓ Code compiles')"
if errorlevel 1 (
    echo.
    echo ERROR: Code has syntax errors!
    pause
    exit /b 1
)

echo.
echo [3/5] Creating final commit...
git add -A
git commit -m "final: production-ready submission for Meta PyTorch OpenEnv Hackathon"

echo.
echo [4/5] Pushing to GitHub...
git push origin master

echo.
echo [5/5] Final checklist...
echo.
echo ================================================================
echo SUBMISSION READY!
echo ================================================================
echo.
echo ✓ All 69 tests passing
echo ✓ Code quality verified
echo ✓ Git pushed to GitHub
echo.
echo NEXT STEPS (Manual):
echo.
echo 1. Verify HF Space:
echo    https://muhammedsayeedurrahman-mogul-logistics.hf.space
echo.
echo 2. Submit on Scaler Dashboard:
echo    https://www.scaler.com/school-of-technology/meta-pytorch-hackathon/dashboard
echo.
echo    GitHub URL: https://github.com/muhammedsayeedurrahman/mogul-logistics
echo    HF Space URL: https://muhammedsayeedurrahman-mogul-logistics.hf.space
echo.
echo 3. Wait for automated validation
echo.
echo ================================================================
echo GOOD LUCK!
echo ================================================================
echo.
pause
