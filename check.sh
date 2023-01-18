echo "<------------ isort ------------>"
isort .
# echo "<------------ black ------------>"
# py -m black .
echo "<------------ mypy ------------>"
mypy .
echo "<------------ pylint ------------>"
pylint **/*.py
