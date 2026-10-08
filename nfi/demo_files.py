import struct
import zlib


def get_pdf_content(lines: list[str]) -> bytes:
	text = " ".join(
		f"({line.replace('(', '[').replace(')', ']')}) Tj 0 -22 Td" for line in lines if line.isascii()
	)
	stream = f"BT /F1 14 Tf 60 760 Td {text} ET".encode()
	objects = [
		b"<< /Type /Catalog /Pages 2 0 R >>",
		b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
		b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
		b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
		b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
	]
	content = b"%PDF-1.4\n"
	offsets = []
	for number, body in enumerate(objects, start=1):
		offsets.append(len(content))
		content += b"%d 0 obj\n%s\nendobj\n" % (number, body)
	xref_offset = len(content)
	content += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
	content += b"".join(b"%010d 00000 n \n" % offset for offset in offsets)
	content += b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (
		len(objects) + 1,
		xref_offset,
	)
	return content


def get_png_content(color: tuple[int, int, int], size: int = 64) -> bytes:
	def get_chunk(kind: bytes, data: bytes) -> bytes:
		return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

	row = b"\x00" + bytes(color) * size
	header = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
	return (
		b"\x89PNG\r\n\x1a\n"
		+ get_chunk(b"IHDR", header)
		+ get_chunk(b"IDAT", zlib.compress(row * size))
		+ get_chunk(b"IEND", b"")
	)
