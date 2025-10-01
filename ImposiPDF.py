from pypdf import PdfReader, PdfWriter
from tkinter import filedialog, messagebox
import tkinter as tk

# Taille finale A4 paysage en points
A4_LANDSCAPE = (842.0, 595.0)  # largeur x hauteur

# Marge extérieure en mm à ajouter
EXTRA_MARGIN_MM = 5  # par exemple 5 mm


# Conversion mm → points
def mm_to_pts(mm):
    return mm * 72 / 25.4


EXTRA_MARGIN = mm_to_pts(EXTRA_MARGIN_MM)


def impose_booklet(input_path, output_path):
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)

        # Ajouter pages blanches pour multiple de 4
        while total_pages % 4 != 0:
            reader.pages.append(writer.add_blank_page(width=421, height=595))
            total_pages += 1

        # Ordre du livret
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

        imposed_order = get_booklet_order(total_pages)

        # Taille d'une demi-page moins marge extérieure
        half_width = A4_LANDSCAPE[0] / 2
        page_w = half_width - EXTRA_MARGIN
        page_h = A4_LANDSCAPE[1]

        for left_idx, right_idx in imposed_order:
            new_page = writer.add_blank_page(width=A4_LANDSCAPE[0], height=A4_LANDSCAPE[1])

            pages_to_merge = [reader.pages[left_idx], reader.pages[right_idx]]
            half_width = A4_LANDSCAPE[0] / 2
            page_height = A4_LANDSCAPE[1]

            for i, page in enumerate(pages_to_merge):
                # Calcul de l'échelle pour que la page remplisse au maximum sa moitié en largeur
                scale_x = half_width / page.mediabox.width
                scale_y = page_height / page.mediabox.height
                scale = min(scale_x, scale_y)

                # Largeur et hauteur après mise à l'échelle
                w_scaled = page.mediabox.width * scale
                h_scaled = page.mediabox.height * scale

                # Coordonnées horizontales
                if i == 0:  # page gauche → espace éventuel à gauche
                    tx = half_width - w_scaled  # aligner à droite de sa moitié
                else:  # page droite → espace éventuel à droite
                    tx = half_width + 0  # commencer au début de la moitié droite (collée à gauche)
                # Coordonnée verticale : centrer
                ty = (page_height - h_scaled) / 2

                # Transformation
                from pypdf import Transformation
                transform = Transformation().scale(scale).translate(tx, ty)
                new_page.merge_transformed_page(page, transform)

        writer.write(output_path)
        messagebox.showinfo("Succès", f"PDF imposé créé : {output_path}")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))


# Interface Tkinter
root = tk.Tk()
root.title("Générateur de livrets PDF")
root.geometry("400x200")


def select_file():
    path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    file_path.set(path)


def convert():
    if not file_path.get():
        messagebox.showwarning("Attention", "Sélectionnez un fichier PDF")
        return
    output = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if output:
        impose_booklet(file_path.get(), output)


file_path = tk.StringVar()
tk.Label(root, text="Sélectionnez un PDF :").pack(pady=10)
tk.Entry(root, textvariable=file_path, width=50).pack()
tk.Button(root, text="Parcourir", command=select_file).pack(pady=5)
tk.Button(root, text="Convertir en livret", command=convert).pack(pady=20)

root.mainloop()
