echo "install requirements"
pip install -r requirements.txt
echo "collect static"
python3.9 manage.py collectstatic