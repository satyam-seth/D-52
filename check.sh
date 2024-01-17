echo "<------------ isort ------------>"
isort ./the_split ./core ./accounts ./records
echo "<------------ black ------------>"
python -m black ./the_split ./core ./accounts ./records
echo "<------------ mypy ------------>"
mypy ./the_split ./core ./accounts ./records
echo "<------------ pylint ------------>"
pylint ./the_split ./core ./accounts ./records
