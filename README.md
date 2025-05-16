Agardata avanza

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the web server
python app.py
```

Open http://localhost:5000 in your browser to view the dynamic chart.
## Docker (optional)

Build and run the container locally:
```bash
docker build -t ascelia-owners .
docker run -p 5000:5000 ascelia-owners
```

## Deploy on Fly.io
1. Install Flyctl: https://fly.io/docs/hands-on/install-flyctl/
2. Authenticate:
   ```bash
   flyctl auth login
   ```
3. Launch (if you haven’t initialized Fly for this app):
   ```bash
   flyctl launch --name ascelia-owners --region iad --dockerfile Dockerfile
   ```
   This creates `fly.toml` and deploys your app.
4. For subsequent deploys:
   ```bash
   flyctl deploy
   ```
5. Open in browser:
   ```bash
   flyctl open
   ```

Your live app will be available at `https://ascelia-owners.fly.dev`.