#!/usr/bin/env python3
from pypdf import PdfReader, PdfWriter, PageObject
import os
import platform
import copy


def mm_to_pt(mm):
    """Convertit des millimètres en points PDF."""
    return mm * 72 / 25.4  # 1 pouce = 25.4 mm, 1 pouce = 72 points


def get_downloads_folder():
    """Retourne le dossier Téléchargements selon le système d’exploitation."""
    home = os.path.expanduser("~")
    system = platform.system()
    if system == "Windows":
        return os.path.join(home, "Downloads")
    elif system == "Darwin":  # macOS
        return os.path.join(home, "Downloads")
    elif system == "Linux":
        if os.path.exists(os.path.join(home, "Téléchargements")):
            return os.path.join(home, "Téléchargements")
        return os.path.join(home, "Downloads")
    return home


def impose_booklet(input_pdf, output_pdf, add_crop_marks=True, bleed_mm=5):
    """Crée un PDF imposé en livret avec fond perdu et vérification des formats."""
    if not os.path.exists(input_pdf):
        print(f"❌ Erreur : le fichier '{input_pdf}' n'existe pas.")
        return

    reader = PdfReader(input_pdf)
    pages = list(reader.pages)
    total_pages = len(pages)

    # Vérifie que toutes les pages ont la même taille
    first_w = pages[0].mediabox.width
    first_h = pages[0].mediabox.height
    for i, page in enumerate(pages[1:], start=2):
        w = page.mediabox.width
        h = page.mediabox.height
        if abs(w - first_w) > 1 or abs(h - first_h) > 1:
            print(f"❌ Erreur : la page {i} a un format différent ({w:.1f}×{h:.1f} pts).")
            print("Merci de fournir un PDF dont toutes les pages ont le même format.")
            return

    writer = PdfWriter()

    # Ajout de pages blanches pour obtenir un multiple de 4
    if total_pages % 4 != 0:
        missing = 4 - (total_pages % 4)
        for _ in range(missing):
            blank_page = PageObject.create_blank_page(width=first_w, height=first_h)
            pages.append(blank_page)
        total_pages += missing

    # Calcul de l'ordre d'imposition (livret)
    imposed_order = []
    for i in range(total_pages // 2):
        if i % 2 == 0:
            imposed_order.append((total_pages - i - 1, i))
        else:
            imposed_order.append((i, total_pages - i - 1))

    # Dimensions finales
    bleed = mm_to_pt(bleed_mm)
    page_width = first_w
    page_height = first_h

    imposed_width = page_width * 2 + 2 * bleed
    imposed_height = page_height + 2 * bleed - mm_to_pt(3)
    half_width = (imposed_width - 2 * bleed) / 2
    half_height = page_height
    offset_x = bleed
    offset_y = bleed

    # Traitement des pages
    for left_idx, right_idx in imposed_order:
        new_page = PageObject.create_blank_page(width=imposed_width, height=imposed_height)

        # --- Page gauche ---
        left_page = copy.deepcopy(pages[left_idx])
        scale_x = half_width / left_page.mediabox.width
        scale_y = half_height / left_page.mediabox.height
        scale = min(scale_x, scale_y)
        left_page.scale_by(scale)
        left_copy = PageObject.create_blank_page(width=half_width, height=half_height)
        left_copy.merge_page(left_page)
        tx = offset_x
        ty = bleed - mm_to_pt(3)
        new_page.merge_translated_page(left_copy, tx=tx, ty=ty)

        # --- Page droite ---
        right_page = copy.deepcopy(pages[right_idx])
        scale_x = half_width / right_page.mediabox.width
        scale_y = half_height / right_page.mediabox.height
        scale = min(scale_x, scale_y)
        right_page.scale_by(scale)
        right_copy = PageObject.create_blank_page(width=half_width, height=half_height)
        right_copy.merge_page(right_page)
        tx = offset_x + half_width
        ty = bleed - mm_to_pt(3)
        new_page.merge_translated_page(right_copy, tx=tx, ty=ty)

        # --- Traits de coupe ---
        if add_crop_marks:
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            from io import BytesIO
            from pypdf import PdfReader as RLReader

            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=(imposed_width, imposed_height))
            c.setStrokeColorRGB(0, 0, 0)
            c.setLineWidth(0.5)
            mark_len = mm * 5

            x_positions = [bleed, half_width + bleed, imposed_width - bleed]
            y_positions = [bleed, imposed_height - bleed]

            for x in x_positions:
                c.line(x, y_positions[0] - mark_len, x, y_positions[0])
                c.line(x, y_positions[1], x, y_positions[1] + mark_len)
            for y in y_positions:
                c.line(x_positions[0] - mark_len, y, x_positions[0], y)
                c.line(x_positions[2], y, x_positions[2] + mark_len, y)

            c.save()
            packet.seek(0)
            overlay = RLReader(packet)
            new_page.merge_page(overlay.pages[0])

        writer.add_page(new_page)

    # Écriture du fichier final
    with open(output_pdf, "wb") as f_out:
        writer.write(f_out)

    print(f"✅ PDF imposé exporté avec succès :\n{output_pdf}")


# === Interface console ===
print("\n\n\n=== 📘 ImposiPDF - Outil d'imposition de pages (par Alice Massart) ===\n")
print("Ce que tu obtiendras :")
print("- Un fichier PDF prêt pour impression en livret")
print("- Format automatiquement adapté (A4, A5, etc.)")
print("- Des traits de coupe automatiques\n")

input_pdf = input("Chemin vers ton fichier PDF (ex: C:\\Users\\TonNom\\Documents\\fichier.pdf)\n-> ").strip()
output_name = input("Nom du fichier de sortie (sans extension)\n-> ").strip()

downloads_dir = get_downloads_folder()
os.makedirs(downloads_dir, exist_ok=True)
output_pdf_path = os.path.join(downloads_dir, f"{output_name}.pdf")

impose_booklet(input_pdf, output_pdf_path, add_crop_marks=True)
