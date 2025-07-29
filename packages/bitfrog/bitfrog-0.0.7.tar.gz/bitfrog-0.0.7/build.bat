@echo off

del /q /s "dist\*"
python -m build
python -m twine upload -r bitfrog dist/*