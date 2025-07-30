# vs_score

A Python package for volleyball match outcome prediction and statistical analysis.

## Installation

```bash
pip install .
```

## Usage

All main modules are located in the `src/vs_score/` directory.

### Data Preparation & Feature Engineering
Run the following scripts in order to clean your data and generate features:

```bash
python src/vs_score/merge_clean.py
python src/vs_score/feature_engineering.py
python src/vs_score/train_model.py
```

### Running the FastAPI Backend
To start the prediction API:

```bash
python src/vs_score/predict_api.py
```

Then open your browser and go to [http://localhost:8000](http://localhost:8000) to use the web interface.

## License
MIT
