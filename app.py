from flask import Flask, request, send_file, jsonify
from pypdf import PdfReader, PdfWriter, Transformation
import tempfile
import os

app = Flask(__name__)

A4_LANDSCAPE = (842.0, 595.0)
EXTRA_MARGIN_MM = 5

def mm_to_pts(mm):
    return mm * 72 / 25.4

EXTRA_MARGIN = mm_to_pts(EXTRA_MARGIN_MM)

def get_booklet_order(n):
    order = []
    left = n - 1
    right = 0
    while left > right:
        order.append((left, right))
        right += 1
        left -= 1
    if left > right:
        order.append((right, left))
        right += 1
        left -= 1
    return order

def impose_booklet(input_stream, output_path):
    reader = PdfReader(input_stream)
    writer = PdfWriter()
    total_pages = len(reader.pages)
    while total_pages % 4 != 0:
        reader.pages.append(writer.add_blank_page(width=421, height=595))
        total_pages += 1
    imposed_order = get_booklet_order(total_pages)
    half_width = A4_LANDSCAPE[0] / 2
    page_w = half_width - EXTRA_MARGIN
    page_h = A4_LANDSCAPE[1]
    for left_idx, right_idx in imposed_order:
        new_page = writer.add_blank_page(width=A4_LANDSCAPE[0], height=A4_LANDSCAPE[1])
        pages_to_merge = [reader.pages[left_idx], reader.pages[right_idx]]
        half_width = A4_LANDSCAPE[0] / 2
        page_height = A4_LANDSCAPE[1]
        for i, page in enumerate(pages_to_merge):
            scale_x = half_width / page.mediabox.width
            scale_y = page_height / page.mediabox.height
            scale = min(scale_x, scale_y)
            w_scaled = page.mediabox.width * scale
            h_scaled = page.mediabox.height * scale
            if i == 0:
                tx = half_width - w_scaled
            else:
                tx = half_width + 0
            ty = (page_height - h_scaled) / 2
            transform = Transformation().scale(scale).translate(tx, ty)
            new_page.merge_transformed_page(page, transform)
    writer.write(output_path)

@app.route('/impose', methods=['POST'])
def impose_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_in, \
         tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_out:
        file.save(temp_in.name)
        temp_in.flush()
        try:
            impose_booklet(temp_in.name, temp_out.name)
            return send_file(temp_out.name, as_attachment=True, download_name='livret.pdf', mimetype='application/pdf')
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.unlink(temp_in.name)
            os.unlink(temp_out.name)

if __name__ == '__main__':
    app.run(debug=True)
