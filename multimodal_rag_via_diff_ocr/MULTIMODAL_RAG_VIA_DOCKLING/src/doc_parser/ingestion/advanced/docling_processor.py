"""Docling document conversion with enrichments."""

import asyncio
from io import BytesIO

from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import ConversionResult, DocumentStream
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions, AcceleratorDevice

from .logging import get_logger

logger = get_logger("docling_processor")

# Global converter instance (lazy-loaded)
_converter: DocumentConverter | None = None


def _get_converter() -> DocumentConverter:
    global _converter
    if _converter is None:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.accelerator_options = AcceleratorOptions(
            device=AcceleratorDevice.CPU,
            num_threads=4,
        )
        pipeline_options.do_table_structure = True
        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_picture_classification = True
        pipeline_options.do_picture_description = True
        pipeline_options.generate_picture_images = True
        pipeline_options.generate_page_images = True
        pipeline_options.images_scale = 2

        _converter = DocumentConverter(format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            InputFormat.IMAGE: PdfFormatOption(pipeline_options=pipeline_options),
        })
    return _converter


async def convert_document(file_bytes: BytesIO, filename: str) -> ConversionResult:
    """Convert a document using Docling (CPU-bound, runs in thread).

    Args:
        file_bytes: BytesIO containing the document.
        filename: Original filename for format detection.

    Returns:
        Docling ConversionResult.
    """
    converter = _get_converter()

    def _convert() -> ConversionResult:
        doc_stream = DocumentStream(name=filename, stream=file_bytes)
        return converter.convert(doc_stream)

    logger.info("Converting document", filename=filename)
    result = await asyncio.to_thread(_convert)
    logger.info("Document converted", filename=filename, pages=len(result.document.pages))
    return result
