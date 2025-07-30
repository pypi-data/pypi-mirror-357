from pdf2image import convert_from_path, pdfinfo_from_path

try:
    pdf_info = pdfinfo_from_path('/Users/hilla/dev/rizzbuzz/arclio-mcp-tooling/packages/google-workspace-mcp/hello.pdf', userpw=None)
    print(pdf_info)
except Exception as e:
    print(f"PDF info error: {e}")

images = convert_from_path("/Users/hilla/dev/rizzbuzz/arclio-mcp-tooling/packages/google-workspace-mcp/hello.pdf", dpi=300)