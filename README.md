# Speaker Diarization API

This project sets up a speaker diarization API using **Django** and **pyannote.audio**. Follow the instructions below to set up the environment, run the Django server, and test the API with a sample `curl` command.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
  - [Setting Up Conda Environment](#setting-up-conda-environment)
  - [Running the Django Application](#running-the-django-application)
- [Testing the Diarization API](#testing-the-diarization-api)
  - [Using `curl` for Testing](#using-curl-for-testing)

---

## Prerequisites

- **Python 3.8 or higher** (Ensure your system is using a compatible version)
- **Conda**: Used for managing the environment.
- **`curl`**: Used to test the API with an audio file.

---

## Setup Instructions

### Setting Up Conda Environment

1. **Create the Conda Environment**:
   - Ensure the `environment.yml` file is in the root folder (same level as `manage.py`).
   - Run the following command to create the environment:
     ```bash
     conda env create -f environment.yml
     ```

2. **Activate the Conda Environment**:
   - After the environment is created, activate it:
     ```bash
     conda activate pyannote-audio
     ```

## Running the Django Application
### Start the Django Development Server:

  -Once the environment is set up, start the server with:
```bash
python manage.py runserver

```

 -The server will start at http://127.0.0.1:8000/.




   
