import fitz  # PyMuPDF
import pdfplumber
import re
import yaml
# import pytesseract
import numpy as np
from transformers import AutoTokenizer, AutoProcessor, AutoModelForImageTextToText
# VisionEncoderDecoderModel, ViTImageProcessor,
from typing import Literal, final
import torch
from PIL import Image
import os
import logging
import traceback
import warnings
from pathlib import Path
from abc import ABC, abstractmethod
import argparse
from PIL import Image
import io
from PIL import Image

model_path = "nanonets/Nanonets-OCR-s"

model = AutoModelForImageTextToText.from_pretrained(
    model_path,
    torch_dtype="auto",
    device_map="auto",
    attn_implementation="flash_attention_2"
)
model.eval()

tokenizer = AutoTokenizer.from_pretrained(model_path)
processor = AutoProcessor.from_pretrained(model_path)


warnings.filterwarnings("ignore")

with open(Path("config/config.yaml").resolve(), "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)


class PDFExtractor(ABC):
    """Abstract base class for PDF extraction."""

    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.setup_logging()

    def setup_logging(self):
        """Set up logging configuration."""
        log_dir = Path(__file__).parent / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{Path(__file__).stem}.log"

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def extract(self) ->  tuple[object, list[object]] | tuple[Literal[''], list[object]] | None:
        """Abstract method for extracting content from PDF."""
        pass


class MarkdownPDFExtractor(PDFExtractor):
    """Class for extracting markdown-formatted content from PDF."""

    BULLET_POINTS = "•◦▪▫●○"

    def __init__(self, pdf_path, output_path= config["OUTPUT_DIR"], page_delimiter= config["PAGE_DELIMITER"]):
        super().__init__(pdf_path)

        self.markdown_content= ""
        self.pdf_filename = Path(pdf_path).stem
        self.output_path= output_path

        output_filepath= f"{Path(self.output_path)}/{self.pdf_filename}.md"
        self.output_filepath= output_filepath

        self.page_delimiter= page_delimiter
        Path(output_path).mkdir(parents=True, exist_ok=True)

        # self.setup_image_captioning()

    # def setup_image_captioning(self):
    #     """Set up the image captioning model."""
    #     try:
    #         self.model = VisionEncoderDecoderModel.from_pretrained(
    #             "nlpconnect/vit-gpt2-image-captioning"
    #         )
    #         self.feature_extractor = ViTImageProcessor.from_pretrained(
    #             "nlpconnect/vit-gpt2-image-captioning"
    #         )
    #         self.tokenizer = AutoTokenizer.from_pretrained(
    #             "nlpconnect/vit-gpt2-image-captioning"
    #         )
    #         self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    #         self.model.to(self.device)
    #         self.logger.info("Image captioning model set up successfully.")
    #     except Exception as e:
    #         self.logger.error(f"Error setting up image captioning model: {e}")
    #         self.logger.exception(traceback.format_exc())

    def extract(self):
        try:
            markdown_content, markdown_pages = self.extract_markdown()
            self.save_markdown(markdown_content)
            self.markdown_content= markdown_content
            self.logger.info(
                f"Markdown content has been saved to {Path(self.output_path)}/{self.pdf_filename}.md"
            )
            return markdown_content, markdown_pages

        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            self.logger.exception(traceback.format_exc())
            return "", []

    def extract_markdown_by_blocks(self):
        """Main method to extract markdown from PDF."""
        try:
            doc = fitz.open(self.pdf_path)
            markdown_content = ""
            markdown_pages = []
            tables = self.extract_tables()
            table_index = 0
            list_counter = 0
            in_code_block = False
            code_block_content = ""
            code_block_lang = None
            prev_line = ""

            for page_num, page in enumerate(doc):
                self.logger.info(f"Processing page {page_num + 1}")
                page_content = ""
                blocks = page.get_text("dict")["blocks"]
                page_height = page.rect.height
                links = self.extract_links(page)

                if len(page.get_images()) > 0 and len(page.get_images()) <= 128:
                    for block in blocks:
                        if block["type"] == 0:  # Text
                            page_content += self.process_text_block(
                                block,
                                page_height,
                                links,
                                list_counter,
                                in_code_block,
                                code_block_content,
                                code_block_lang,
                                prev_line,
                            )
                        elif block["type"] == 1:  # Image
                            page_content += self.process_image_block(page, block)

                else:
                    for block in blocks:
                        if block["type"] == 0:  # Text
                            page_content += self.process_text_block(
                                block,
                                page_height,
                                links,
                                list_counter,
                                in_code_block,
                                code_block_content,
                                code_block_lang,
                                prev_line,
                            )

                # Insert tables at their approximate positions
                while (
                    table_index < len(tables)
                    and tables[table_index]["page"] == page.number
                ):
                    page_content += (
                        "\n\n"
                        + self.table_to_markdown(tables[table_index]["content"])
                        + "\n\n"
                    )
                    table_index += 1

                markdown_pages.append(self.post_process_markdown(page_content))
                markdown_content += page_content + config["PAGE_DELIMITER"]

            markdown_content = self.post_process_markdown(markdown_content)
            return markdown_content, markdown_pages
        except Exception as e:
            self.logger.error(f"Error extracting markdown: {e}")
            self.logger.exception(traceback.format_exc())
            return "", []


    def ocr_page_with_nanonets_s(self, pil_image, model, processor, max_new_tokens: int | None = None):
        prompt = """Extract the text from the above document as if you were reading it naturally. Return the tables in html format. Return the equations in LaTeX representation. If there is an image in the document and image caption is not present, add a small description of the image inside the <img></img> tag; otherwise, add the image caption inside <img></img>. Watermarks should be wrapped in brackets. Ex: <watermark>OFFICIAL COPY</watermark>. Page numbers should be wrapped in brackets. Ex: <page_number>14</page_number> or <page_number>9/22</page_number>. Prefer using ☐ and ☑ for check boxes."""
        if max_new_tokens is None:
            max_new_tokens= 4096

        # image = Image.open(image_path)
        image = pil_image
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ]},
        ]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt")
        inputs = inputs.to(model.device)

        output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]

        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        return output_text[0]



    def extract_markdown(self):
        """
        Extracts all possible text content from a PDF page, concatenating it
        from direct text blocks, OCR from embedded image blocks, and OCR from
        full-page raster images (scanned pages).

        Returns:
            list: A list of strings, where each string is the comprehensive text
                  for a corresponding page. Returns an empty list if an error occurs.
        """

        """taken from self:
            pdf_path (str): The path to the input PDF file.
            output_path (str): Directory to save debug output (like rendered images).
        """

        all_pages_text = []
        the_text= ""

        try:
            doc = fitz.open(self.pdf_path)
            logging.info(f"Opened PDF: {self.pdf_path}")

            tables = self.extract_tables()
            table_index = 0
            list_counter = 0
            in_code_block = False
            code_block_content = ""
            code_block_lang = None
            prev_line = ""

            for page_num, page in enumerate(doc):
                page_text_content = []
                page_has_searchable_text = False

                logging.info(f"\nProcessing page {page_num + 1}...")

                # --- Phase 1: Extract text from direct text blocks and process embedded images ---
                blocks = page.get_text('dict')['blocks']
                text_blocks_content = []
                image_block_text_content = []

                page_height = page.rect.height
                links = self.extract_links(page)

                for block_num, block in enumerate(blocks):
                    if block['type'] == 0:  # Text block
                        page_has_searchable_text = True
                        text_blocks_content.append(self.process_text_block(
                            block,
                            page_height,
                            links,
                            list_counter,
                            in_code_block,
                            code_block_content,
                            code_block_lang,
                            prev_line,
                        ))

                        # for line in block['lines']:
                        #     for span in line['spans']:
                        #         text_blocks_content.append(span['text'])
                    elif block['type'] == 1:  # Image block
                        logging.info(f"  Found embedded image block (Page {page_num+1}, Block {block_num+1})")
                        img_data = block['image']
                        img_ext = block['ext']

                        try:
                            # Attempt OCR on the embedded image block
                            pil_image = Image.open(io.BytesIO(img_data))
                            # ocr_text_from_block_image = pytesseract.image_to_string(pil_image)
                            ocr_text_from_block_image= self.ocr_page_with_nanonets_s(pil_image, model, processor, max_new_tokens=15000)

                            if ocr_text_from_block_image.strip():
                                logging.info(f"    OCR found text in embedded image block.")
                                image_block_text_content.append(ocr_text_from_block_image.strip())
                            else:
                                # If no OCR text, use the caption
                                # caption = self.caption_image(pil_image)
                                # if caption:
                                #     logging.info(f"    No OCR text, using caption for embedded image block.")
                                #     image_block_text_content.append(caption)
                                # else:
                                #     logging.info(f"    No OCR text and no caption for embedded image block.")

                                # a) captioning sucks, b) no need
                                image_block_text_content.append("An Image")

                        # except pytesseract.TesseractNotFoundError:
                        #     logging.warning("    Tesseract-OCR not found. Skipping OCR for embedded image block.")
                            # caption = self.process_image_block(page, block)
                            # if caption: image_block_text_content.append(caption)

                            # image_block_text_content.append("An Image")
                        except Exception as e:
                            logging.error(f"    Error processing embedded image block for OCR/caption: {e}")
                            # caption = self.process_image_block(page, block)
                            # if caption: image_block_text_content.append(caption)
                            image_block_text_content.append("An Image")


                # Insert tables at their approximate positions
                while (
                    table_index < len(tables)
                    and tables[table_index]["page"] == page.number
                ):
                    page_text_content += (
                        "\n\n"
                        + self.table_to_markdown(tables[table_index]["content"])
                        + "\n\n"
                    )
                    table_index += 1

                # Add content from text blocks
                if text_blocks_content:
                    page_text_content.append(" ".join(text_blocks_content))

                # Add content from image blocks
                if image_block_text_content:
                    page_text_content.append("\n".join(image_block_text_content))


                # --- Phase 2: OCR the entire page IF it seems to be a scanned image ---
                # We check if page_has_searchable_text is False or if the amount of text
                # is very small, suggesting it might be mostly a scanned page.
                # A threshold of 50 characters is arbitrary; adjust as needed.
                current_text_len = len(" ".join(page_text_content).strip())

                if not page_has_searchable_text or current_text_len < 50:
                    logging.info(f"  Page {page_num + 1} appears to be a scanned image or has minimal text. Attempting full-page OCR.")
                    try:
                        # Render the page as a high-resolution image (e.g., 300 DPI)
                        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                        img_bytes = pix.tobytes("png")

                        pil_image = Image.open(io.BytesIO(img_bytes))

                        # Perform OCR on the entire page image
                        # ocr_text_from_page = pytesseract.image_to_string(pil_image)
                        ocr_text_from_page= self.ocr_page_with_nanonets_s(pil_image, model, processor, max_new_tokens=15000)

                        if ocr_text_from_page.strip():
                            logging.info(f"  Successfully extracted text via full-page OCR.")
                            page_text_content.append(ocr_text_from_page.strip())
                        else:
                            logging.info(f"  Full-page OCR yielded no text for page {page_num+1}.")

                    # except pytesseract.TesseractNotFoundError:
                    #     logging.warning("  Tesseract-OCR not found. Skipping full-page OCR for this page.")
                    except Exception as e:
                        logging.error(f"  Error during full-page OCR on page {page_num+1}: {e}")
                else:
                    logging.info(f"  Page {page_num + 1} has sufficient searchable text; skipping full-page OCR.")


                # Concatenate all collected text for the current page
                final_page_text = "\n".join(filter(None, page_text_content)).strip() # Use filter(None, ...) to remove empty strings
                all_pages_text.append(self.post_process_markdown(final_page_text))
                the_text += final_page_text + self.page_delimiter

                logging.info(f"  Comprehensive text for page {page_num + 1} (first 200 chars):\n{final_page_text[:200]}...")

                print("\npage done\n")
                print(final_page_text)


            doc.close()
            return the_text, all_pages_text

        except fitz.FileNotFoundError:
            logging.error(f"PDF file not found: {self.pdf_path}")
            return []
        except Exception as e:
            logging.critical(f"An unexpected error occurred: {e}")
            return []


    def extract_tables(self):
        """Extract tables from PDF using pdfplumber."""
        tables = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_number, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if len(page_tables) > 128:
                        continue
                    for table in page_tables:
                        tables.append({"page": page_number, "content": table})
            self.logger.info(f"Extracted {len(tables)} tables from the PDF.")
        except Exception as e:
            self.logger.error(f"Error extracting tables: {e}")
            self.logger.exception(traceback.format_exc())
        return tables

    def table_to_markdown(self, table):
        """Convert a table to markdown format."""
        if not table:
            return ""

        try:
            table = [
                ["" if cell is None else str(cell).strip() for cell in row]
                for row in table
            ]
            col_widths = [max(len(cell) for cell in col) for col in zip(*table)]

            markdown = ""
            for i, row in enumerate(table):
                formatted_row = [
                    cell.ljust(col_widths[j]) for j, cell in enumerate(row)
                ]
                markdown += "| " + " | ".join(formatted_row) + " |\n"

                if i == 0:
                    markdown += (
                        "|"
                        + "|".join(["-" * (width + 2) for width in col_widths])
                        + "|\n"
                    )

            return markdown
        except Exception as e:
            self.logger.error(f"Error converting table to markdown: {e}")
            self.logger.exception(traceback.format_exc())
            return ""

    def perform_ocr(self, image):
        """Perform OCR on the given image."""
        try:
            # ocr_result = pytesseract.image_to_string(
            #     image
            # )
            ocr_result= self.ocr_page_with_nanonets_s(image, model, processor, max_new_tokens=15000)


            return ocr_result.strip()
        except Exception as e:
            self.logger.error(f"Error performing OCR: {e}")
            self.logger.exception(traceback.format_exc())
            return ""

    def caption_image(self, image):
        """Generate a caption for the given image."""
        try:
            ocr_text = self.perform_ocr(image)
            if ocr_text:
                return ocr_text

            # Convert image to RGB if it's not already
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Ensure the image is in the correct shape
            image = np.array(image).transpose(2, 0, 1)  # Convert to (C, H, W) format

            inputs = self.feature_extractor(images=image, return_tensors="pt").to(
                self.device
            )
            pixel_values = inputs.pixel_values

            generated_ids = self.model.generate(pixel_values, max_length=30)
            generated_caption = self.tokenizer.batch_decode(
                generated_ids, skip_special_tokens=True
            )[0]
            return generated_caption.strip()
        except Exception as e:
            self.logger.error(f"Error captioning image: {e}")
            self.logger.exception(traceback.format_exc())
            return ""

    def clean_text(self, text):
        """Clean the given text by removing extra spaces."""
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def apply_formatting(self, text, flags):
        """Apply markdown formatting to the given text based on flags."""
        text = text.strip()
        if not text:
            return text

        is_bold = flags & 2**4
        is_italic = flags & 2**1
        is_monospace = flags & 2**3
        is_superscript = flags & 2**0
        is_subscript = flags & 2**5

        if is_monospace:
            text = f"`{text}`"
        elif is_superscript and not bool(re.search(r"\s+", text)):
            text = f"^{text}^"
        elif is_subscript and not bool(re.search(r"\s+", text)):
            text = f"~{text}~"

        if is_bold and is_italic:
            text = f"***{text}***"
        elif is_bold:
            text = f"**{text}**"
        elif is_italic:
            text = f"*{text}*"

        return f" {text} "

    def is_bullet_point(self, text):
        """Check if the given text is a bullet point."""
        return text.strip().startswith(tuple(self.BULLET_POINTS))

    def convert_bullet_to_markdown(self, text):
        """Convert a bullet point to markdown format."""
        text = re.sub(r"^\s*", "", text)
        return re.sub(f"^[{re.escape(self.BULLET_POINTS)}]\s*", "- ", text)

    def is_numbered_list_item(self, text):
        """Check if the given text is a numbered list item."""
        return bool(re.match(r"^\d+\s{0,3}[.)]", text.strip()))

    def convert_numbered_list_to_markdown(self, text, list_counter):
        """Convert a numbered list item to markdown format."""
        text = re.sub(r"^\s*", "", text)
        return re.sub(r"^\d+\s{0,3}[.)]", f"{list_counter}. ", text)

    def is_horizontal_line(self, text):
        """Check if the given text represents a horizontal line."""
        return bool(re.match(r"^[_-]+$", text.strip()))

    def extract_links(self, page):
        """Extract links from the given page."""
        links = []
        try:
            for link in page.get_links():
                if link["kind"] == 2:  # URI link
                    links.append({"rect": link["from"], "uri": link["uri"]})
            self.logger.info(f"Extracted {len(links)} links from the page.")
        except Exception as e:
            self.logger.error(f"Error extracting links: {e}")
            self.logger.exception(traceback.format_exc())
        return links

    def detect_code_block(self, prev_line, current_line):
        """Detect if the current line starts a code block."""
        patterns = {
            "python": [
                (
                    r"^(?:from|import)\s+\w+",
                    r"^(?:from|import|def|class|if|for|while|try|except|with)\s",
                ),
                (r"^(?:def|class)\s+\w+", r"^\s{4}"),
                (r"^\s{4}", r"^\s{4,}"),
            ],
            "javascript": [
                (
                    r"^(?:function|const|let|var)\s+\w+",
                    r"^(?:function|const|let|var|if|for|while|try|catch|class)\s",
                ),
                (r"^(?:if|for|while)\s*\(", r"^\s{2,}"),
                (r"^\s{2,}", r"^\s{2,}"),
            ],
            "html": [
                (
                    r"^<(!DOCTYPE|html|head|body|div|p|a|script|style)",
                    r"^<(!DOCTYPE|html|head|body|div|p|a|script|style)",
                ),
                (r"^<\w+.*>$", r"^\s{2,}<"),
                (r"^\s{2,}<", r"^\s{2,}<"),
            ],
            "shell": [
                (r"^(?:\$|\#)\s", r"^(?:\$|\#)\s"),
                (r"^[a-z_]+\s*=", r"^[a-z_]+\s*="),
            ],
            "bash": [
                (
                    r"^(?:#!/bin/bash|alias|export|source)\s",
                    r"^(?:#!/bin/bash|alias|export|source|echo|read|if|for|while|case|function)\s",
                ),
                (r"^(?:if|for|while|case|function)\s", r"^\s{2,}"),
                (r"^\s{2,}", r"^\s{2,}"),
            ],
            "cpp": [
                (
                    r"^#include\s*<",
                    r"^(?:#include|using|namespace|class|struct|enum|template|typedef)\s",
                ),
                (r"^(?:class|struct|enum)\s+\w+", r"^\s{2,}"),
                (r"^\s{2,}", r"^\s{2,}"),
            ],
            "java": [
                (
                    r"^(?:import|package)\s+\w+",
                    r"^(?:import|package|public|private|protected|class|interface|enum)\s",
                ),
                (r"^(?:public|private|protected)\s+class\s+\w+", r"^\s{4,}"),
                (r"^\s{4,}", r"^\s{4,}"),
            ],
            "json": [
                (r"^\s*{", r'^\s*["{[]'),
                (r'^\s*"', r'^\s*["}],?$'),
                (r"^\s*\[", r"^\s*[}\]],?$"),
            ],
        }

        for lang, pattern_pairs in patterns.items():
            for prev_pattern, curr_pattern in pattern_pairs:
                if re.match(prev_pattern, prev_line.strip()) and re.match(
                    curr_pattern, current_line.strip()
                ):
                    return lang

        return None

    def process_text_block(
        self,
        block,
        page_height,
        links,
        list_counter,
        in_code_block,
        code_block_content,
        code_block_lang,
        prev_line,
    ):
        """Process a text block and convert it to markdown."""
        try:
            block_rect = block["bbox"]
            if block_rect[1] < 50 or block_rect[3] > page_height - 50:
                return ""  # Skip headers and footers

            block_text = ""
            last_y1 = None
            last_font_size = None

            for line in block["lines"]:
                line_text = ""
                curr_font_size = [span["size"] for span in line["spans"]]

                for span in line["spans"]:
                    text = span["text"]
                    font_size = span["size"]
                    flags = span["flags"]
                    span_rect = span["bbox"]

                    if self.is_horizontal_line(text):
                        line_text += "\n---\n"
                        continue

                    text = self.clean_text(text)

                    if text.strip():
                        header_level = self.get_header_level(font_size)
                        if header_level > 0:
                            text = f"\n{'#' * header_level} {text}\n\n"

                        else:
                            is_list_item = self.is_bullet_point(
                                text
                            ) or self.is_numbered_list_item(text)

                            if is_list_item:
                                marker, content = re.split(
                                    r"(?<=^[•◦▪▫●○\d.)])\s*", text, 1
                                )
                                formatted_content = self.apply_formatting(
                                    content, flags
                                )
                                text = f"{marker} {formatted_content}"
                            else:
                                text = self.apply_formatting(text, flags)

                    for link in links:
                        if fitz.Rect(span_rect).intersects(link["rect"]):
                            text = f"[{text.strip()}]({link['uri']})"
                            break

                    line_text += text

                if last_y1 is not None:
                    avg_last_font_size = (
                        sum(last_font_size) / len(last_font_size)
                        if last_font_size
                        else 0
                    )
                    avg_current_font_size = sum(curr_font_size) / len(curr_font_size)
                    font_size_changed = (
                        abs(avg_current_font_size - avg_last_font_size) > 1
                    )

                    if abs(line["bbox"][3] - last_y1) > 2 or font_size_changed:
                        block_text += "\n"

                block_text += self.clean_text(line_text) + " "
                last_font_size = curr_font_size
                last_y1 = line["bbox"][3]

            markdown_content = ""
            lines = block_text.split("\n")
            for i, line in enumerate(lines):
                clean_line = self.clean_text(line)

                if not in_code_block:
                    code_lang = self.detect_code_block(prev_line, clean_line)
                    if code_lang:
                        in_code_block = True
                        code_block_lang = code_lang
                        code_block_content = prev_line + "\n" + clean_line + "\n"
                        prev_line = clean_line
                        continue

                if in_code_block:
                    code_block_content += clean_line + "\n"
                    if (
                        i == len(lines) - 1
                        or self.detect_code_block(clean_line, lines[i + 1])
                        != code_block_lang
                    ):
                        markdown_content += (
                            f"```{code_block_lang}\n{code_block_content}```\n\n"
                        )
                        in_code_block = False
                        code_block_content = ""
                        code_block_lang = None
                else:
                    if self.is_bullet_point(clean_line):
                        markdown_content += "\n" + self.convert_bullet_to_markdown(
                            clean_line
                        )
                        list_counter = 0
                    elif self.is_numbered_list_item(clean_line):
                        list_counter += 1
                        markdown_content += (
                            "\n"
                            + self.convert_numbered_list_to_markdown(
                                clean_line, list_counter
                            )
                        )
                    else:
                        markdown_content += f"{clean_line}\n"
                        list_counter = 0

                prev_line = clean_line

            return markdown_content + "\n"
        except Exception as e:
            self.logger.error(f"Error processing text block: {e}")
            self.logger.exception(traceback.format_exc())
            return ""

    def process_image_block(self, page, block):
        """Process an image block and convert it to markdown."""
        try:
            image_rect = block["bbox"]
            zoom_x = 2.0  # horizontal zoom
            zoom_y = 2.0  # vertical zoom
            mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension
            pix = page.get_pixmap(clip=image_rect, matrix=mat, alpha=False)
            image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            if image.width < 20 or image.height < 20:
                return ""

            image_filename = (
                f"{self.pdf_filename}_image_{int(page.number)+1}_{block['number']}.png"
            )
            image_path = (
                Path(self.output_path) / image_filename
            )  # Convert to Path object
            image.save(image_path, "PNG", optimize=True, quality=95)
            caption = self.caption_image(image)
            if not caption:
                caption = (
                    f"{self.pdf_filename}_image_{int(page.number)+1}_{block['number']}"
                )

            return f"![{caption}]({image_path})\n\n"  # image_path is now a Path object
        except Exception as e:
            self.logger.error(f"Error processing image block: {e}")
            self.logger.exception(traceback.format_exc())
            return ""

    def get_header_level(self, font_size):
        """Determine header level based on font size."""
        if font_size > 24:
            return 1
        elif font_size > 20:
            return 2
        elif font_size > 18:
            return 3
        elif font_size > 16:
            return 4
        elif font_size > 14:
            return 5
        elif font_size > 12:
            return 6
        else:
            return 0

    def post_process_markdown(self, markdown_content):
        """Post-process the markdown content."""
        try:
            markdown_content = re.sub(
                r"\n{3,}", "\n\n", markdown_content
            )  # Remove excessive newlines
            markdown_content = re.sub(
                r"(\d+)\s*\n", "", markdown_content
            )  # Remove page numbers
            markdown_content = re.sub(
                r" +", " ", markdown_content
            )  # Remove multiple spaces
            markdown_content = re.sub(
                r"\s*(---\n)+", "\n\n---\n", markdown_content
            )  # Remove duplicate horizontal lines

            def remove_middle_headers(match):
                line = match.group(0)
                # Keep the initial header and remove all subsequent '#' characters
                return re.sub(
                    r"(^#{1,6}\s).*?(?=\n)",
                    lambda m: m.group(1)
                    + re.sub(r"#", "", m.group(0)[len(m.group(1)) :]),
                    line,
                )

            markdown_content = re.sub(
                r"^#{1,6}\s.*\n",
                remove_middle_headers,
                markdown_content,
                flags=re.MULTILINE,
            )  # Remove headers in the middle of lines
            return markdown_content
        except Exception as e:
            self.logger.error(f"Error post-processing markdown: {e}")
            self.logger.exception(traceback.format_exc())
            return markdown_content

    def save_markdown(self, markdown_content):
        """Save the markdown content to a file."""
        try:
            os.makedirs(Path(self.output_path), exist_ok=True)
            with open(
                self.output_filepath,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(markdown_content)
            self.logger.info("Markdown content saved successfully.")
        except Exception as e:
            self.logger.error(f"Error saving markdown content: {e}")
            self.logger.exception(traceback.format_exc())


def main():
    parser = argparse.ArgumentParser(
        description="Extract markdown-formatted content from a PDF file."
    )
    parser.add_argument("--pdf_path", help="Path to the input PDF file", required=True)
    args = parser.parse_args()

    extractor = MarkdownPDFExtractor(args.pdf_path)
    markdown_pages = extractor.extract()
    return markdown_pages


if __name__ == "__main__":
    main()
