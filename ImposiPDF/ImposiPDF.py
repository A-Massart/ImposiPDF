#!/usr/bin/env python3
import os
import platform
import copy
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter, PageObject


# =====================
#   UTILITAIRES PDF
# =====================
def mm_to_pt(mm):
    return mm * 72 / 25.4


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


def impose_booklet(input_pdf, output_pdf, add_crop_marks=True, bleed_mm=5):
    if not os.path.exists(input_pdf):
        raise FileNotFoundError(f"Le fichier '{input_pdf}' n'existe pas.")

    reader = PdfReader(input_pdf)
    pages = list(reader.pages)
    total_pages = len(pages)

    first_w = pages[0].mediabox.width
    first_h = pages[0].mediabox.height

    for i, page in enumerate(pages[1:], start=2):
        if (abs(page.mediabox.width - first_w) > 1 or
                abs(page.mediabox.height - first_h) > 1):
            raise ValueError(f"Page {i} avec dimension différente.")

    writer = PdfWriter()

    if total_pages % 4 != 0:
        for _ in range(4 - total_pages % 4):
            pages.append(PageObject.create_blank_page(width=first_w, height=first_h))
        total_pages = len(pages)

    imposed_order = []
    for i in range(total_pages // 2):
        if i % 2 == 0:
            imposed_order.append((total_pages - i - 1, i))
        else:
            imposed_order.append((i, total_pages - i - 1))

    bleed = mm_to_pt(bleed_mm)
    imposed_width = first_w * 2 + 2 * bleed
    imposed_height = first_h + 2 * bleed - mm_to_pt(3)
    half_width = (imposed_width - 2 * bleed) / 2
    half_height = first_h

    for left_idx, right_idx in imposed_order:
        new_page = PageObject.create_blank_page(width=imposed_width, height=imposed_height)

        # LEFT
        left_page = copy.deepcopy(pages[left_idx])
        scale = min(half_width / left_page.mediabox.width, half_height / left_page.mediabox.height)
        left_page.scale_by(scale)
        left_copy = PageObject.create_blank_page(width=half_width, height=half_height)
        left_copy.merge_page(left_page)
        new_page.merge_translated_page(left_copy, bleed, bleed - mm_to_pt(3))

        # RIGHT
        right_page = copy.deepcopy(pages[right_idx])
        scale = min(half_width / right_page.mediabox.width, half_height / right_page.mediabox.height)
        right_page.scale_by(scale)
        right_copy = PageObject.create_blank_page(width=half_width, height=half_height)
        right_copy.merge_page(right_page)
        new_page.merge_translated_page(right_copy, bleed + half_width, bleed - mm_to_pt(3))

        # Crop marks
        if add_crop_marks:
            from reportlab.pdfgen import canvas
            from reportlab.lib.units import mm
            from io import BytesIO
            from pypdf import PdfReader as RLReader

            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=(imposed_width, imposed_height))
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

    with open(output_pdf, "wb") as f:
        writer.write(f)


# =====================
#   INTERFACE MODERNE
# =====================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("ImposiPDF")
root.geometry("850x500")
root.resizable(False, False)

pdf_var = ctk.StringVar()
output_var = ctk.StringVar()
bleed_var = ctk.StringVar(value="5")
crop_var = ctk.BooleanVar(value=True)

preview_image = None
preview_label = None

# ---------- RESET INTERFACE ----------
def reset_interface():
    pdf_var.set("")         # Réinitialise le chemin PDF
    output_var.set("")      # Réinitialise le nom du fichier de sortie
    bleed_var.set("5")      # Remet le fond perdu par défaut
    crop_var.set(True)      # Remet les traits de coupe cochés
    preview_label.configure(image="", text="Aucun PDF sélectionné")  # Reset miniature

# ---------- MINIATURE PDF via PyMuPDF ----------
def load_preview(pdf_path):
    global preview_image, preview_label
    if not os.path.exists(pdf_path):
        return
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]  # première page
        zoom = 2  # DPI x2 pour meilleure qualité
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail((300, 400))
        preview_image = ImageTk.PhotoImage(img)
        preview_label.configure(image=preview_image, text="")
        doc.close()
    except Exception as e:
        preview_label.configure(text=f"Impossible de charger la miniature\n{e}")


# ---------- CHOIX DU FICHIER ----------
def choose_file():
    filename = filedialog.askopenfilename(
        title="Choisir un PDF",
        filetypes=[("PDF", "*.pdf")]
    )
    pdf_var.set(filename)
    if filename:
        load_preview(filename)


# ---------- IMPOSITION ----------
def run_imposition():
    try:
        input_pdf = pdf_var.get()
        out_name = output_var.get().strip()
        if not input_pdf:
            messagebox.showerror("Erreur", "Veuillez sélectionner un PDF.")
            return
        if not out_name:
            messagebox.showerror("Erreur", "Veuillez entrer un nom de fichier de sortie.")
            return
        downloads = get_downloads_folder()
        output_pdf = os.path.join(downloads, out_name + ".pdf")
        impose_booklet(input_pdf, output_pdf, add_crop_marks=crop_var.get(), bleed_mm=int(bleed_var.get()))
        messagebox.showinfo("Succès", f"PDF généré dans :\n{output_pdf}")
        reset_interface()
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


# =====================
#   UI LAYOUT
# =====================

# ---- LEFT SIDEBAR ----
left = ctk.CTkFrame(root, corner_radius=10, fg_color="#1a1a1a")
left.pack(side="left", fill="y", padx=15, pady=15)

ctk.CTkLabel(left, text="PARAMÈTRES", font=("Arial", 20, "bold")).pack(pady=20)
ctk.CTkLabel(left, text="PDF source :").pack(anchor="w", padx=20)
ctk.CTkEntry(left, textvariable=pdf_var, width=240).pack(padx=20, pady=5)
ctk.CTkButton(left, text="Parcourir", command=choose_file).pack(pady=5)

ctk.CTkLabel(left, text="Nom du PDF exporté :").pack(anchor="w", padx=20, pady=(20, 0))
ctk.CTkEntry(left, textvariable=output_var, width=240).pack(padx=20, pady=5)

ctk.CTkCheckBox(left, text="Ajouter les traits de coupe", variable=crop_var).pack(pady=15)

ctk.CTkLabel(left, text="Fond perdu (mm) :").pack(anchor="w", padx=20)
ctk.CTkEntry(left, textvariable=bleed_var, width=80).pack(padx=20, pady=5)

ctk.CTkButton(left, text="Imposer et exporter", command=run_imposition, height=40).pack(pady=30)


# ---- RIGHT PREVIEW ----
right = ctk.CTkFrame(root, corner_radius=10, fg_color="#0f0f0f")
right.pack(side="right", fill="both", expand=True, padx=15, pady=15)

ctk.CTkLabel(right, text="APERÇU PDF", font=("Arial", 20, "bold")).pack(pady=10)
preview_label = ctk.CTkLabel(right, text="Aucun PDF sélectionné", font=("Arial", 16))
preview_label.pack(pady=20)

root.mainloop()
