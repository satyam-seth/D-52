echo "<------------ isort ------------>"
isort ./the_split ./core ./accounts ./records
echo "<------------ black ------------>"
python -m black ./the_split ./core ./accounts ./records
echo "<------------ mypy ------------>"
mypy ./the_split ./core ./accounts ./records
echo "<------------ pylint ------------>"
pylint ./the_split ./core ./accounts ./records
echo "<------------ test ------------>"
coverage run --source='.' manage.py test 
echo "<------------ code coverage ------------>"
coverage html
