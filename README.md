# Amazon Orders Information System
Automatically retrieves and displays order customization information from Amazon Seller Central using a downloaded TSV file. The app processes order data, downloads customization files (images, JSON metadata), and presents everything in an interactive web table.


## Installation
1. Clone this repository:
```bash
git clone https://github.com/kzrob/sc-pod
cd sc-pod
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the Flask development server:
```bash
python3 app.py
```
The app will start on `http://localhost:3001`


## Production Deployment

For production use, uncomment the `waitress` line in `app.py`:

```python
# Replace this:
app.run(debug=True, host="0.0.0.0", port=3001)

# With this:
serve(app, host="0.0.0.0", port=3001, threads=10)
```

Then run:
```bash
python app.py
```


## Usage
1. Download your TSV file from Amazon Seller Central
2. Start the application
3. Upload your TSV file
4. View and interact with your data


## Project Structure
```
sc-pod/
├── app.py                 # Flask web application
├── backend.py             # TSV processing and data extraction logic
├── definitions.py         # Path constants and configuration
├── requirements.txt       # Python dependencies
├── data.db                # SQLite database (created on first upload)
├── log.txt                # Error logs
├── downloads/             # Downloaded customization files (created automatically)
│   └── <order-item-id>/   # One folder per order containing .jpg, .json, .svg, .xml
├── static/                # Frontend assets
│   ├── app.js             # JavaScript for table interactivity
│   └── style.css          # Styling
├── templates/             # HTML templates
│   └── index.html         # Main page template
└── images/                # Static logo/product images
    ├── Jubope/
    └── CYR/
```
