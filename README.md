# Project Setup
## 1. Set `OPENAI_API_KEY` and `TOGETHER_API_KEY` in `backend/.env`
```
OPENAI_API_KEY=xxxxx
TOGETHER_API_KEY=xxxxx
```

## 2. Create conda environment
```
conda env create -f env.yml
```

# Run our Vision Crafter app

1. In a new terminal, run the following command to start the Flask server:

```
python -m backend.run
```

2. Open a new terminal, navigate to the frontend directory:
```bash
cd frontend
```
Install the npm dependencies:
```bash
npm install
```
Then to start the React development server:
```bash
npm start
```

This open the app on your browser at `http://localhost:3000/`.