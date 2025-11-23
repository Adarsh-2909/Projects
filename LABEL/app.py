from flask import Flask, request, send_file
import pandas as pd
import io

app = Flask(__name__)

# --- 1. FRONT-END TEMPLATE ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Excel Column D Processor (Sorted)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 50px; background-color: #f4f4f4; }
        .container { max-width: 600px; margin: auto; padding: 30px; background-color: white; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #007bff; margin-bottom: 25px; }
        input[type="file"] { display: block; margin: 20px auto; padding: 10px; border: 2px dashed #ccc; border-radius: 6px; width: 90%; box-sizing: border-box; }
        button { background-color: #28a745; color: white; padding: 12px 15px; border: none; border-radius: 6px; cursor: pointer; width: 100%; font-size: 18px; transition: background-color 0.3s; }
        button:hover { background-color: #1e7e34; }
        .message { margin-top: 15px; padding: 15px; border-radius: 4px; display: none; text-align: center; font-weight: bold; }
        .loading { background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Excel Column D Extractor Tool (Sorted)</h1>
        <p style="text-align: center; color: #666;">Upload your XLS/XLSX file to extract, split, and consolidate data from Column D across all sheets. The final list will be sorted alphabetically.</p>
        <form id="upload-form" action="/process" method="post" enctype="multipart/form-data">
            <input type="file" name="excel_file" id="excel-file-input" accept=".xls,.xlsx,.xltx" required>
            <button type="submit">Analyze and Download Sorted Data</button>
            <div id="loading-message" class="message loading">Processing file... This may take a moment for large files.</div>
        </form>
    </div>

    <script>
        document.getElementById('upload-form').addEventListener('submit', function(e) {
            document.getElementById('loading-message').style.display = 'block';
        });
    </script>
</body>
</html>
"""

# --- 2. CORE DATA PROCESSING LOGIC ---
def process_excel_data(file_content_bytes):
    all_data = []

    try:
        xls_file = pd.ExcelFile(io.BytesIO(file_content_bytes))
    except Exception as e:
        return f"Error reading file. Details: {e}"

    for sheet_name in xls_file.sheet_names:
        df = xls_file.parse(sheet_name).dropna(how='all')

        if len(df.columns) < 4:
            continue

        df_d = df.iloc[:, [3]].copy()
        df_d.columns = ['Extracted_Words']
        df_d.dropna(subset=['Extracted_Words'], inplace=True)

        df_d['Extracted_Words'] = df_d['Extracted_Words'].astype(str)

        processed_list = []

        for value in df_d['Extracted_Words']:
            value = value.strip()

            # RULE 1: Remove text after colon
            if ":" in value:
                value = value.split(":")[0].strip()

            # Split by comma
            parts = [p.strip() for p in value.split(",") if p.strip()]

            for p in parts:
                # RULE 2: Handle "X to Y" patterns
                if " to " in p:
                    try:
                        prefix = "".join([c for c in p if not c.isdigit()]).replace("to", "").strip()
                        nums = p.split("to")
                        start = int(nums[0].split()[-1])
                        end = int(nums[1])

                        for num in range(start, end + 1):
                            processed_list.append(f"{prefix} {num}".strip())
                    except:
                        processed_list.append(p)
                else:
                    processed_list.append(p)

        df_exploded = pd.DataFrame(processed_list, columns=['Extracted_Words'])
        all_data.append(df_exploded)

    if not all_data:
        return "No valid data found in Column D."

    final_df = pd.concat(all_data, ignore_index=True)
    final_df.sort_values(by='Extracted_Words', inplace=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        final_df.to_excel(writer, index=False, sheet_name='Consolidated_D_Column')

    output.seek(0)
    return output


# --- 3. ROUTES ---
@app.route('/')
def index():
    return HTML_TEMPLATE


@app.route('/process', methods=['POST'])
def process_file():
    if 'excel_file' not in request.files or request.files['excel_file'].filename == '':
        return "Error: No file uploaded.", 400

    file_bytes = request.files['excel_file'].read()
    processed_output = process_excel_data(file_bytes)

    if isinstance(processed_output, str):
        return processed_output, 400

    return send_file(
        processed_output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='processed_column_D_sorted_data.xlsx'
    )


if __name__ == '__main__':
    app.run(debug=True, port=9000)

