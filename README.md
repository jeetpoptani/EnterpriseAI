# Image Describer (Groq)

This project describes what is in an image using a Groq vision model.

## FastAPI Payload API

Run the API server:

```bash
uvicorn api:app --reload
```

Send payload:

```bash
curl -X POST "http://127.0.0.1:8000/describe" \
	-F "image=@test.jpg" \
	-F "model=auto"
```

Send video payload:

```bash
curl -X POST "http://127.0.0.1:8000/describe-video" \
	-F "video=@test.mp4" \
	-F "model=auto" \
	-F "max_frames=4" \
	-F "summary_model=llama-3.3-70b-versatile"
```

Health check:

```bash
curl "http://127.0.0.1:8000/health"
```

## 1) Install

```bash
pip install -r requirements.txt
```

## 2) Set API key

PowerShell:

```powershell
$env:GROQ_API_KEY="your_groq_api_key"
```

## 3) Run

```bash
python image_describer.py "path/to/your-image.jpg"
```

Optional model override:

```bash
python image_describer.py "path/to/your-image.jpg" --model "meta-llama/llama-4-scout-17b-16e-instruct"
```
