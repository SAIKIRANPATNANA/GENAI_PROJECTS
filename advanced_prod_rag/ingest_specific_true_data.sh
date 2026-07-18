#!/bin/bash

# Ensure you are in the project's root directory
# cd /home/user/snap/Downloads/AI-SECURITY-LEARNING/8hr-MARATHON-deployment

# Create a temporary directory for the files
TEMP_INGEST_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_INGEST_DIR"

# Copy the two failed files to the temporary directory
cp DATA/true_data/cronjobs.docx "$TEMP_INGEST_DIR/"
cp DATA/true_data/architecture.pptx "$TEMP_INGEST_DIR/"

echo "Starting ingestion for cronjobs.docx and architecture.pptx..."

# Run the ingestion processor on the temporary directory
# The 'true' argument sets the source_type for these documents
python -m app.ingestion.processor "$TEMP_INGEST_DIR" true

# Clean up the temporary directory
echo "Cleaning up temporary directory: $TEMP_INGEST_DIR"
rm -rf "$TEMP_INGEST_DIR"

echo "Ingestion attempt for cronjobs.docx and architecture.pptx completed."
echo "Please check the output for any new errors or successes."
