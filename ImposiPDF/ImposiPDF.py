#!/usr/bin/env python3
import os
import platform
import copy
from tkinter import filedialog, messagebox
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter, PageObject

# =====================
#   FORMATS PDF
# =====================

def mm_to_pt(mm):
    return mm * 72 / 25.4

PDF_FORMATS = {
    "A5": (mm_to_pt(148), mm_to_pt(210)),
    "A4": (mm_to_pt(210), mm_to_pt(297)),
    "A3": (mm_to_pt(297), mm_to_pt(420)),
    "A2": (mm_to_pt(420), mm_to_pt(594)),
}

# =====================
#   UTILITAIRES
# =====================

def get_downloads_folder():
    home = os.path.expanduser("~")
    system = platform.system()
    if system == "Windows":
        return os.path.join(home, "Downloads")
    elif system == "Darwin":
        return os.path.join(home, "Downloads")
    elif system == "Linux":
        if os.path.exists(os.path.join(home, "Téléchargements")):
            return os.path.join(home, "Téléchargements")
        return os.path.join(home, "Downloads")
    return home

# =====================
#   IMPOSITION AVEC REDIMENSION PROPORTIONNEL
# =====================

def impose_booklet(input_pdf, output_pdf, add_crop_marks=True, bleed_mm=5, output_format="A4"):
    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Le fichier '{input_pdf}' n'existe pas.")

    # Mapping utilisateur -> taille d'une page (la moitié de la feuille)
    PAGE_MAPPING = {
        "A5": "A5",
        "A4": "A5",
        "A3": "A4",
        "A2": "A3",
    }
    page_format = PAGE_MAPPING.get(output_format, "A5")
    if page_format not in PDF_FORMATS:
        raise ValueError(f"Format interne inconnu : {page_format}")

    page_w, page_h = PDF_FORMATS[page_format]
    bleed = mm_to_pt(bleed_mm)

    # Taille finale = format utilisateur (paysage)
    target_w, target_h = PDF_FORMATS[output_format]
    imposed_width = max(target_w, target_h)
    imposed_height = min(target_w, target_h)

    # Espace dispo pour chaque demi-page
    usable_w = (imposed_width - 2 * bleed) / 2
    usable_h = imposed_height - 2 * bleed

    # Lecture PDF source
    reader = PdfReader(input_pdf)
    pages = list(reader.pages)
    total_pages = len(pages)
    first_w, first_h = pages[0].mediabox.width, pages[0].mediabox.height

    for i, page in enumerate(pages[1:], start=2):
        if abs(page.mediabox.width - first_w) > 1 or abs(page.mediabox.height - first_h) > 1:
            raise ValueError(f"Page {i} a un format différent.")

    # Compléter à un multiple de 4
    if total_pages % 4 != 0:
        for _ in range(4 - total_pages % 4):
            pages.append(PageObject.create_blank_page(width=first_w, height=first_h))
        total_pages = len(pages)

    # Ordre livret
    imposed_order = []
    for i in range(total_pages // 2):
        if i % 2 == 0:
            imposed_order.append((total_pages - i - 1, i))
        else:
            imposed_order.append((i, total_pages - i - 1))

    writer = PdfWriter()

    # Création pages imposées
    for left_idx, right_idx in imposed_order:
        new_page = PageObject.create_blank_page(width=imposed_width, height=imposed_height)

        # ---- Page gauche ----
        left_page = copy.deepcopy(pages[left_idx])
        scale_left = min(usable_w / left_page.mediabox.width, usable_h / left_page.mediabox.height)
        left_page.scale_by(scale_left)

        # ---- Page droite ----
        right_page = copy.deepcopy(pages[right_idx])
        scale_right = min(usable_w / right_page.mediabox.width, usable_h / right_page.mediabox.height)
        right_page.scale_by(scale_right)

        # Centrage des 2 pages collées
        total_content_width = left_page.mediabox.width + right_page.mediabox.width
        start_x = (imposed_width - total_content_width) / 2
        start_y = (imposed_height - max(left_page.mediabox.height, right_page.mediabox.height)) / 2

        # Position gauche
        left_copy = PageObject.create_blank_page(width=left_page.mediabox.width, height=left_page.mediabox.height)
        left_copy.merge_page(left_page)
        new_page.merge_translated_page(left_copy, tx=start_x, ty=start_y)

        # Position droite
        right_copy = PageObject.create_blank_page(width=right_page.mediabox.width, height=right_page.mediabox.height)
        right_copy.merge_page(right_page)
        new_page.merge_translated_page(right_copy, tx=start_x + left_page.mediabox.width, ty=start_y)

        # ---- Traits de coupe ----
        if add_crop_marks:
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            from io import BytesIO
            from pypdf import PdfReader as RLReader

            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=(imposed_width, imposed_height))
            c.setLineWidth(0.5)
            mark_len = mm * 5

            # Page gauche
            lx0, ly0 = start_x, start_y
            lx1, ly1 = start_x + left_page.mediabox.width, start_y + left_page.mediabox.height
            c.line(lx0, ly0, lx0 + mark_len, ly0)
            c.line(lx0, ly0, lx0, ly0 + mark_len)
            c.line(lx1, ly0, lx1 - mark_len, ly0)
            c.line(lx0, ly1, lx0 + mark_len, ly1)
            c.line(lx0, ly1, lx0, ly1 - mark_len)
            c.line(lx1, ly1, lx1 - mark_len, ly1)

            # Page droite
            rx0, ry0 = start_x + left_page.mediabox.width, start_y
            rx1, ry1 = rx0 + right_page.mediabox.width, ry0 + right_page.mediabox.height
            c.line(rx0, ry0, rx0 + mark_len, ry0)
            c.line(rx1, ry0, rx1 - mark_len, ry0)
            c.line(rx1, ry0, rx1, ry0 + mark_len)
            c.line(rx0, ry1, rx0 + mark_len, ry1)
            c.line(rx1, ry1, rx1 - mark_len, ry1)
            c.line(rx1, ry1, rx1, ry1 - mark_len)

            c.save()
            packet.seek(0)
            overlay = RLReader(packet)
            new_page.merge_page(overlay.pages[0])

        writer.add_page(new_page)

    # Export PDF final
    with open(output_pdf, "wb") as f:
        writer.write(f)

# =====================
#   INTERFACE UI
# =====================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("ImposiPDF")
root.geometry("900x650")
root.resizable(False, False)

pdf_var = ctk.StringVar()
output_var = ctk.StringVar()
bleed_var = ctk.StringVar(value="5")
crop_var = ctk.BooleanVar(value=True)
format_var = ctk.StringVar(value="A4")

preview_image = None

# Créer un placeholder transparent (1x1 px) pour initialiser le label
placeholder_img = CTkImage(
    light_image=Image.new("RGB", (1, 1), (0, 0, 0)),
    dark_image=Image.new("RGB", (1, 1), (0, 0, 0)),
    size=(1, 1)
)

# -------------------- UI PANEL GAUCHE --------------------
left = ctk.CTkFrame(root, corner_radius=10, fg_color="#1a1a1a")
left.pack(side="left", fill="y", padx=15, pady=15)

ctk.CTkLabel(left, text="PARAMÈTRES", font=("Arial", 20, "bold")).pack(pady=20)
ctk.CTkLabel(left, text="PDF source :").pack(anchor="w", padx=20)
ctk.CTkEntry(left, textvariable=pdf_var, width=240).pack(padx=20, pady=5)
ctk.CTkButton(left, text="Parcourir", command=lambda: choose_file()).pack(pady=5)
ctk.CTkLabel(left, text="Nom du PDF exporté :").pack(anchor="w", padx=20, pady=(20, 0))
ctk.CTkEntry(left, textvariable=output_var, width=240).pack(padx=20, pady=5)
ctk.CTkLabel(left, text="Format de sortie :").pack(anchor="w", padx=20, pady=(20, 0))
ctk.CTkOptionMenu(left, variable=format_var, values=list(PDF_FORMATS.keys())).pack(padx=20, pady=5)
ctk.CTkCheckBox(left, text="Ajouter les traits de coupe", variable=crop_var).pack(pady=15)
ctk.CTkLabel(left, text="Fond perdu (mm) :").pack(anchor="w", padx=20)
ctk.CTkEntry(left, textvariable=bleed_var, width=80).pack(padx=20, pady=5)
ctk.CTkButton(left, text="Imposer et exporter", command=lambda: run_imposition(), height=40).pack(pady=30)

# -------------------- UI PANEL DROIT --------------------
right = ctk.CTkFrame(root, corner_radius=10, fg_color="#0f0f0f")
right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

ctk.CTkLabel(right, text="APERÇU PDF", font=("Arial", 20, "bold")).pack(pady=10)

preview_label = ctk.CTkLabel(
    right,
    text="Aucun PDF sélectionné",
    font=("Arial", 16),
    image=placeholder_img
)
preview_label.pack(pady=20)

# =====================
#   FONCTIONS UI
# =====================

def reset_interface():
    pdf_var.set("")
    output_var.set("")
    bleed_var.set("5")
    crop_var.set(True)
    format_var.set("A4")
    preview_label.configure(image=placeholder_img, text="Aucun PDF sélectionné")

def load_preview(pdf_path):
    global preview_image
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail((300, 400))
        preview_image = CTkImage(light_image=img, dark_image=img, size=img.size)
        preview_label.configure(image=preview_image, text="")
        doc.close()
    except Exception as e:
        preview_label.configure(text=f"Miniature impossible\n{e}")

def choose_file():
    filename = filedialog.askopenfilename(title="Choisir un PDF", filetypes=[("PDF", "*.pdf")])
    pdf_var.set(filename)
    if filename:
        load_preview(filename)

def run_imposition():
    try:
        input_pdf = pdf_var.get()
        out_name = output_var.get().strip()
        if not input_pdf:
            messagebox.showerror("Erreur", "Sélectionne un PDF.")
            return
        if not out_name:
            messagebox.showerror("Erreur", "Entre un nom de fichier.")
            return
        downloads = get_downloads_folder()
        output_pdf = os.path.join(downloads, out_name + ".pdf")
        impose_booklet(
            input_pdf,
            output_pdf,
            add_crop_marks=crop_var.get(),
            bleed_mm=int(bleed_var.get()),
            output_format=format_var.get()
        )
        messagebox.showinfo("Succès", f"PDF généré dans :\n{output_pdf}")
        reset_interface()
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# =====================
#   LANCEMENT APP
# =====================

root.mainloop()
