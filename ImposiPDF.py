#!/usr/bin/env python3

from pypdf import PdfReader, PdfWriter, PageObject
import os

def mm_to_pt(mm):
    return mm * 72 / 25.4  # 1 pouce = 25.4 mm, 72 pt = 1 pouce

def impose_booklet(input_pdf, output_pdf, add_crop_marks=True, bleed_mm=5):
    if not os.path.exists(input_pdf):
        print(f"Erreur : le fichier '{input_pdf}' n'existe pas.")
        return

    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    total_pages = len(reader.pages)

    # Ajout de pages blanches si nécessaire pour avoir un multiple de 4
    if total_pages % 4 != 0:
        missing = 4 - (total_pages % 4)
        for _ in range(missing):
            blank_page = PageObject.create_blank_page(
                width=reader.pages[0].mediabox.width,
                height=reader.pages[0].mediabox.height
            )
            reader.pages.append(blank_page)
        total_pages += missing

    # Calcul de l'ordre d'imposition
    imposed_order = []
    for i in range(total_pages // 2):
        if i % 2 == 0:
            imposed_order.append((total_pages - i - 1, i))
        else:
            imposed_order.append((i, total_pages - i - 1))

    # Dimensions exactes A4 paysage
    A4_WIDTH = mm_to_pt(297)
    A4_HEIGHT = mm_to_pt(210)
    bleed = mm_to_pt(bleed_mm)

    # Chaque demi-page prend exactement la moitié de l'A4, moins le bleed
    half_width = (A4_WIDTH - 2 * bleed) / 2
    half_height = A4_HEIGHT - 2 * bleed

    # Offset pour centrer les demi-pages
    offset_x = bleed
    offset_y = bleed

    for left_idx, right_idx in imposed_order:
        new_page = PageObject.create_blank_page(width=A4_WIDTH, height=A4_HEIGHT)

        # --- Page gauche ---
        page_left = PageObject.create_blank_page(width=half_width, height=half_height)
        page_left.merge_page(reader.pages[left_idx])
        page_left.scale_to(half_width, half_height)
        new_page.merge_translated_page(page_left, tx=offset_x, ty=offset_y)

        # --- Page droite ---
        page_right = PageObject.create_blank_page(width=half_width, height=half_height)
        page_right.merge_page(reader.pages[right_idx])
        page_right.scale_to(half_width, half_height)
        new_page.merge_translated_page(page_right, tx=offset_x + half_width, ty=offset_y)

        # Ajout des traits de coupe
        if add_crop_marks:
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            from io import BytesIO

            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=(A4_WIDTH, A4_HEIGHT))
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(0.5)

            mark_len = mm * 5

            # coins externes gauche / droite (comme dans ton code original)
            x_positions = [bleed, half_width + bleed, A4_WIDTH - bleed]
            y_positions = [bleed, A4_HEIGHT - bleed]

            for x in x_positions:
                c.line(x, y_positions[0] - mark_len, x, y_positions[0])
                c.line(x, y_positions[1], x, y_positions[1] + mark_len)

            for y in y_positions:
                c.line(x_positions[0] - mark_len, y, x_positions[0], y)
                c.line(x_positions[2], y, x_positions[2] + mark_len, y)

            c.save()
            packet.seek(0)
            overlay = PdfReader(packet)
            new_page.merge_page(overlay.pages[0])

        writer.add_page(new_page)

    with open(output_pdf, 'wb') as f_out:
        writer.write(f_out)

    print(f"✅ PDF imposé exporté : {output_pdf}")

# Titre
print("\n=== ImposiPDF - Outil d'imposition de pages développé par Bidule ===\n"
      "Ce que tu obtiendras :\n"
      "- fichier pdf cahier avec impsoition des pages\n"
      "- traits de coupes\n")
# Inputs simplifiés
input_pdf = input("Chemin vers ton fichier PDF\n(ex: C:/Users/TonNom/Documents/fichier.pdf)\n-> ")
output_pdf = input("Nom du fichier de sortie (sans extension): ")

# Les traits de coupe sont activés par défaut
impose_booklet(input_pdf, f"{output_pdf}.pdf", add_crop_marks=True)
