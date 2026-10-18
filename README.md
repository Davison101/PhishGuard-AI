# PhishGuard AI — Local Phishing URL Classifier

A small web-style dashboard for a classroom demonstration of AI as a cybersecurity defender. It runs on your Windows PC and opens in your normal web browser at `http://localhost:8501`.

## Easiest setup on Windows

1. Install **Python 3.11 (64-bit)** from the official Python website: https://www.python.org/downloads/release/python-3119/ . If the installer offers **Add Python to PATH**, select it.
2. Extract the ZIP file into a normal folder, for example `C:\Users\YourName\Documents\PhishGuardAI`. Do not run it while it is still inside the ZIP archive.
3. Double-click `run_windows.bat`.
4. The first run creates a private Python environment and installs the required packages. This can take some time and needs an internet connection.
5. The app downloads the pretrained model from Hugging Face the first time it is analyzed. Once running, it opens in your default browser. If it does not open automatically, visit `http://localhost:8501`.
6. Use **Use legitimate example** or **Use phishing example**, then click **Analyze URL**.

Keep the black terminal window open while using the app. Close it with `Ctrl+C` or close the terminal window to stop the local server.

## Manual setup

Open Command Prompt in the extracted project folder and run:

```bat
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Then open `http://localhost:8501` in a browser.

## What it does

- Analyzes the URL text with `CrabInHoney/urlbert-tiny-v4-phishing-classifier`.
- Displays the predicted category and each model class score.
- Adds a separate checklist of basic URL warning signs.
- Runs on CPU, so a graphics card is not required.

## Safety and limitations

- The app **does not open or visit the URL**. It sends the URL string to the local model.
- The model's output can be wrong. A high legitimate-like score is not proof a site is safe.
- The warning-sign checklist uses simple rules and is **not** an explanation of the model's internal reasoning.
- Treat this as an educational prototype, not a production security product.

## Model source

Model card and labels: https://huggingface.co/CrabInHoney/urlbert-tiny-v4-phishing-classifier
>>>>>>> d6e072007a3db52c791c7de3683214bf65cfe9a2
=======
# PhishGuard-AI
>>>>>>> d6e072007a3db52c791c7de3683214bf65cfe9a2
