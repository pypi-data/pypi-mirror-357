import os
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, ttk
import re
from decimal import Decimal, InvalidOperation
import platform

# Currency list
CURRENCY_SYMBOLS = list('₦$€£¥₹₽฿₩₫₪₴₲')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


# Extract amounts from text
def extract_amounts(text, selected_symbol=None):
    pattern = r'([' + ''.join(re.escape(sym) for sym in CURRENCY_SYMBOLS) + r'])(\s?\d[\d,]*\.?\d*)'
    matches = re.findall(pattern, text)

    currency_map = {}
    for symbol, number in matches:
        if selected_symbol and symbol != selected_symbol:
            continue
        clean_number = number.replace(',', '').strip()
        try:
            amount = Decimal(clean_number)
            currency_map.setdefault(symbol, []).append(amount)
        except InvalidOperation:
            continue
    return currency_map

# Calculation logic
def calculate(values, operation):
    if not values:
        return Decimal(0)
    if operation == 'Sum':
        return sum(values)
    elif operation == 'Product':
        result = Decimal(1)
        for v in values:
            result *= v
        return result
    elif operation == 'Average':
        return sum(values) / len(values)

# Main action
def run_extraction():
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("No Input", "Please paste some text to analyze.")
        return

    selected_currency = currency_var.get().strip() or None
    operation = operation_var.get()

    results = extract_amounts(text, selected_currency)
    output_box.delete("1.0", tk.END)

    if not results:
        output_box.insert(tk.END, "No currency values found.\n")
        return

    for symbol, values in results.items():
        result = calculate(values, operation)
        output_box.insert(tk.END, f"Currency: {symbol}\n")
        output_box.insert(tk.END, f"  ➤ Count: {len(values)}\n")
        output_box.insert(tk.END, f"  ➤ {operation}: {symbol}{result:,.2f}\n\n")

# Export result
def export_result():
    content = output_box.get("1.0", tk.END).strip()
    if not content:
        messagebox.showinfo("Nothing to Export", "No results to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                             filetypes=[("Text files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Exported", f"Results saved to:\n{file_path}")

# Clear everything
def clear_all():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)
    currency_var.set("")

# GUI setup
app = tk.Tk()
app.title("Amount Extractor v2 by CRYPT_ATU")
if  platform.system() == "windows":
    app.iconbitmap(resource_path("assets/gui_image.ico"))
app.geometry("800x650")
app.configure(bg="#1e1e1e")

header_logo = tk.PhotoImage(file=resource_path("assets/gui_logo.png"))
header = tk.Label(app, text="💸 Amount Extractor v2 by CRYPT_ATU", font=("Helvetica", 20, "bold"), fg="lime", bg="#1e1e1e", image=header_logo)
#header.image = header_logo
header.pack(pady=10)

input_box = scrolledtext.ScrolledText(app, height=8, width=90, font=("Consolas", 11), bg="#252526", fg="white", insertbackground='white')
input_box.pack(pady=10)

controls_frame = tk.Frame(app, bg="#1e1e1e")
controls_frame.pack(pady=5)

# Operation Dropdown
tk.Label(controls_frame, text="Operation:", fg="white", bg="#1e1e1e").grid(row=0, column=0, padx=5)
operation_var = ttk.Combobox(controls_frame, values=["Sum", "Product", "Average"], state="readonly", width=12)
operation_var.grid(row=0, column=1, padx=5)
operation_var.set("Sum")

# Currency Input
tk.Label(controls_frame, text="Currency Filter (Optional):", fg="white", bg="#1e1e1e").grid(row=0, column=2, padx=5)
currency_var = tk.StringVar()
currency_entry = tk.Entry(controls_frame, textvariable=currency_var, width=5)
currency_entry.grid(row=0, column=3, padx=5)

# Buttons
buttons_frame = tk.Frame(app, bg="#1e1e1e")
buttons_frame.pack(pady=10)

tk.Button(buttons_frame, text="Extract", command=run_extraction, bg="green", fg="white", width=12).grid(row=0, column=0, padx=10)
tk.Button(buttons_frame, text="Export to File", command=export_result, bg="#0066cc", fg="white", width=12).grid(row=0, column=1, padx=10)
tk.Button(buttons_frame, text="Clear", command=clear_all, bg="red", fg="white", width=12).grid(row=0, column=2, padx=10)

output_box = scrolledtext.ScrolledText(app, height=15, width=90, font=("Consolas", 11), bg="#1e1e1e", fg="cyan")
output_box.pack(pady=10)

footer = tk.Label(app, text="Author: CRYPT_ATU • Version 2.0", fg="gray", bg="#1e1e1e")
footer.pack(pady=5)

app.mainloop()
