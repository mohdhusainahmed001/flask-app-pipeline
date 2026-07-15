*Flask Application*

**app.py**
Your actual Flask application — defines routes and request handling logic. This is the file Gunicorn points to (app:app) when serving the app in production, and what pytest imports to test against.

**test_app.py**
Unit tests for app.py, run by pytest in the Unit Tests stage. Uses Flask's test client to simulate requests without needing a real server running.
requirements.txt

***Pins the exact Python dependencies (Flask, Gunicorn, pytest, etc.) so every environment — your laptop, Jenkins, the Docker image — installs identical versions. Used by pip install -r requirements.txt in multiple pipeline stages.***

**setup.py**
Packaging metadata that lets python setup.py sdist bdist_wheel build your app into a distributable Python package (.tar.gz + .whl). Used in the Build Artifact stage, then uploaded to Nexus's pypi-hosted repo via twine.

**Dockerfile**
Instructions for building the container image that will actually run your Flask app in production: installs dependencies, copies your code in, and starts Gunicorn as the entrypoint. Used in the Docker Build stage.

**Dockerfile.jenkins**
A separate Dockerfile — not for your app at all. This one builds your customized Jenkins image, baking in Docker CLI, Python, Ansible, and the community.docker collection so Jenkins has everything the pipeline needs without manual container setup each time. Used with docker compose build jenkins, not part of the app's CI/CD stages.

**sonar-project.properties**
Configuration read by the sonar-scanner CLI during the SonarQube Analysis stage — tells SonarQube the project key, which source paths to scan, and which to exclude (e.g. tests/**, venv/**).

**Jenkinsfile**
The actual pipeline definition — every stage (Checkout, tests, SonarQube, artifact build, Nexus pushes, Docker build, Ansible deploy) lives here. This is what Jenkins reads and executes top to bottom.

**ansible/inventory.ini**
Tells Ansible where to deploy — in your case, localhost with ansible_connection=local, meaning Ansible runs its deployment tasks on the same machine rather than SSH-ing to a remote server.

**ansible/deploy.yml**
The actual deployment playbook — pulls the Docker image just pushed to Nexus, stops/removes any old running container, and starts a fresh one with the new image. This is the final step of your pipeline, executed by the Deploy with Ansible stage.