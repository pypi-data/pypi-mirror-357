import os
from magic_pdf.data.data_reader_writer import FileBasedDataWriter, FileBasedDataReader
from magic_pdf.data.dataset import PymuDocDataset
from magic_pdf.model.doc_analyze_by_custom_model import doc_analyze
from magic_pdf.config.enums import SupportedPdfParseMethod


class PdfProcessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PdfProcessor, cls).__new__(cls)
        return cls._instance

    def process_pdf(self, pdf_file_name):
        name_without_suff = os.path.basename(pdf_file_name).split(".")[0]
        print("Processing PDF: " + name_without_suff)

        local_image_dir = "uploaded_files/images"
        local_md_dir = "uploaded_files/markdown"

        os.makedirs(local_image_dir, exist_ok=True)
        os.makedirs(local_md_dir, exist_ok=True)

        image_writer = FileBasedDataWriter(local_image_dir)
        md_writer = FileBasedDataWriter(local_md_dir)

        reader = FileBasedDataReader("")
        pdf_bytes = reader.read(pdf_file_name)

        # 处理流程
        ds = PymuDocDataset(pdf_bytes)
        markdown_path = os.path.join(local_md_dir, f"{name_without_suff}.md")  # 完整路径
        image_dir = os.path.basename(local_image_dir)  # 保持相对路径为 "images"

        if ds.classify() == SupportedPdfParseMethod.OCR:
            ds.apply(doc_analyze, ocr=True).pipe_ocr_mode(image_writer).dump_md(
                md_writer,
                os.path.basename(markdown_path),  # 文件名部分
                image_dir
            )
        else:
            ds.apply(doc_analyze, ocr=False).pipe_txt_mode(image_writer).dump_md(
                md_writer,
                os.path.basename(markdown_path),  # 文件名部分
                image_dir
            )

        with open(markdown_path, "r", encoding='utf-8') as f:
            markdown_content = f.read()

        return markdown_content

pdf_processor = PdfProcessor()

# 使用示例
if __name__ == "__main__":
    # pdf_processor = PdfProcessor()
    print(pdf_processor.process_pdf(
        "/home/caocaiyu/datamax-service/backend/uploaded_files/fde1daee-e899-4e93-87ff-706234c399c3/20250227132500_5447d25cbf094a3295f9d52d3408a048.pdf"
    ))
