# Subhopper
Subhopper is a tool that helps you gather all subdomains based on the provided domain.

## Running the file directly

Install dependencies:
```
pip3 install -r requirements.txt
```

Run the app:
```
python3 app.py
```

Go to [localhost:5000](http://localhost:5000) and search for subdomains of any domain.


## Running in Docker container
```
docker build -t subhopper .
```

```
docker run -p 80:5000 --detach subhopper
```

Go to [localhost:5000](http://localhost:5000) and search for subdomains of any domain.
