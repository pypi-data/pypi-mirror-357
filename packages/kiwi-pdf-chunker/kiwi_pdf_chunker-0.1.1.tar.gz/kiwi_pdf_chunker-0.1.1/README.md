# CV Document Chunker

A Python package for parsing PDF document layouts using YOLO models, chunking content based on layout, and optionally performing OCR.

## Features

- Convert PDF documents to images for processing.
- Detect document layout elements (e.g., paragraphs, tables, figures) using YOLO.
- Process and refine bounding boxes.
- Chunk document content based on detected layout.
- **(Optional)** Perform OCR on detected elements using Azure Document Intelligence.
- Save structured document data (layouts, chunks, OCR text) in JSON format.
- Get paragraph embeddings using OpenAI embedder 

## Installation

### Prerequisites

- Python 3.10+
- Pip package manager
- (Optional but Recommended) CUDA-capable GPU for YOLO model inference acceleration.

### Steps

1.  **Install the Package:**
    ```bash
    # pip install cv-doc-chunker
    ```

## User-Provided Data

This package requires the user to provide certain data externally:

1.  **Input Directory (`input/`):** Place the PDF documents you want to process in a directory (e.g., `input/`). You will need to provide the path to your input file(s) when using the package.
2.  **Models Directory (`models/`):** Download the necessary YOLO model(s) (e.g., `doclayout_yolo_docstructbench_imgsz1024.pt`) and place them in a dedicated directory (e.g., `models/`). The path to this directory (or the specific model file) will be needed by the parser.

## Usage

Provide examples of how to import and use your library functions or the command-line tool.

**Example (Conceptual Python Usage):**

```python
from cv_doc_chunker import PDFProcessor

# --- User Configuration ---
input_pdf_path = "path/to/your/input/document.pdf" # Path to user's PDF
model_path = "path/to/your/models/doclayout_yolo.pt" # Path to user's model
output_dir = "path/to/your/output/" # Directory to save results


parser = PDFParser(ocr = True, embed = True, yolo_model_path = model_path, azure_key = "api key for azure ocr",
                   azure_endpoint = "api endpoint for azure ocr", openai_api_key = openai_api_key)

# --- OR ---
# For Azure OpenAI embeddings, you would use these arguments instead:
# azure_openai_api_key=azure_openai_api_key,
# azure_openai_api_version=azure_openai_api_version,
# azure_openai_endpoint=azure_openai_endpoint

results = parser.parse_document(input_pdf_path, output_dir=output_dir, use_tesseract = True)

```
## Understanding the Output

After running the parser, the following outputs will typically be available in the specified `output_dir`:

1.  `{your-document}_parsed.json`: JSON file containing the detected document structure (element labels, coordinates, confidence).
2.  `{your-document}_annotations/`: Directory containing annotated images showing the detected elements for each page (if `generate_annotations=True`).
3.  `{your-document}_boxes/`: Directory containing individual images for each detected element, organized by page number (if `save_bounding_boxes=True`). This is required for OCR.
4.  **`{your-document}_sorted_text.json`**: (Only if `ocr=True`) JSON file containing the extracted text for each element, sorted according to the structure defined in `_parsed.json`.

If debug mode is enabled (`debug_mode=True`), additional debug images might be saved, typically in a `debug/` subdirectory within the `output_dir`, showing intermediate steps of the parsing process.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.