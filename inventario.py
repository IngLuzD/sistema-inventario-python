import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import glob
from datetime import datetime

# --- DATOS ---
inventario = []
archivo_actual = ""
ARCHIVO_VENTAS = "ventas_diarias.json"

def seleccionar_pdv():
    global archivo_actual, inventario
    pdv = simpledialog.askstring("SISTEMA DE IMPULSO", "¿En qué PDV trabajarás hoy?")
    if not pdv:
        if not archivo_actual: root.destroy()
        return
    archivo_actual = f"inventario_{pdv.lower().replace(' ', '_')}.json"
    cargar_datos(); actualizar_lista()
    root.title(f"SISTEMA DE IMPULSO E INVENTARIOS - {pdv.upper()}")

def cargar_datos():
    global inventario
    if os.path.exists(archivo_actual):
        try:
            with open(archivo_actual, "r", encoding='utf-8') as f:
                inventario = json.load(f)
        except: inventario = []
    else: inventario = []

def guardar_datos():
    if archivo_actual:
        with open(archivo_actual, "w", encoding='utf-8') as f:
            json.dump(inventario, f, indent=4, ensure_ascii=False)

# --- REPORTE PROFESIONAL ---
def reporte_diario_pdv():
    if not os.path.exists(ARCHIVO_VENTAS):
        messagebox.showinfo("Reporte", "No hay ventas registradas.")
        return

    hoy = datetime.now().strftime("%Y-%m-%d")
    pdv_nombre = archivo_actual.replace("inventario_", "").replace(".json", "").upper()
    resumen = {}; total_dia = 0
    
    with open(ARCHIVO_VENTAS, "r", encoding='utf-8') as f:
        ventas = json.load(f)
        
    for v in ventas:
        if v['fecha'] == hoy and v['pdv'] == pdv_nombre:
            p = v['producto']
            resumen[p] = resumen.get(p, [0, 0])
            resumen[p][0] += v['cantidad']
            resumen[p][1] += v['total']
            total_dia += v['total']

    if not resumen:
        messagebox.showinfo("Aviso", "No hay ventas registradas hoy en este punto.")
        return

    # DISEÑO DE FACTURA PARA EL ARCHIVO
    linea = "------------------------------------------"
    f_txt = f"      SISTEMA DE IMPULSO E INVENTARIOS    \n"
    f_txt += f"           CIERRE DE VENTAS DIARIO        \n"
    f_txt += f"{linea}\n"
    f_txt += f"PDV: {pdv_nombre}\n"
    f_txt += f"FECHA: {hoy}\n"
    f_txt += f"{linea}\n"
    f_txt += f"{'PRODUCTO':<20} | {'CANT':<4} | {'SUBTOTAL':<10}\n"
    f_txt += f"{linea}\n"
    
    for prod, d in resumen.items():
        f_txt += f"{prod[:20]:<20} | {d[0]:<4} | ${d[1]:,.0f}\n"
        
    f_txt += f"{linea}\n"
    f_txt += f"TOTAL VENTA DEL DÍA: ${total_dia:,.0f}\n"
    f_txt += f"{linea}\n"
    f_txt += f"        ¡GRACIAS POR TU LABOR HOY!        "

    # Guardar reporte
    nom_archivo = f"REPORTE_{pdv_nombre}_{hoy}.txt"
    with open(nom_archivo, "w", encoding="utf-8") as f:
        f.write(f_txt)

    # Mostrar en pantalla
    v_rep = tk.Toplevel()
    v_rep.title("Cierre Generado")
    t = tk.Text(v_rep, font=("Courier New", 10), padx=10, pady=10)
    t.pack()
    t.insert(tk.END, f_txt)
    messagebox.showinfo("Éxito", f"Reporte guardado como {nom_archivo}")

# --- OPERACIONES ---
def actualizar_lista():
    lista_vis.delete(0, tk.END)
    for p in inventario:
        status = "☕ "
        if p['cantidad'] <= 5: status = "⚠️ STOCK BAJO: "
        item = f"{status}{p['nombre'].upper()} ({p['marca']}) | Stock: {p['cantidad']}"
        lista_vis.insert(tk.END, item)
        if p['cantidad'] <= 5:
            lista_vis.itemconfig(tk.END, {'fg': 'white', 'bg': '#d32f2f'})

def registrar_venta():
    nombre = entry_venta_nom.get().strip().lower()
    try:
        cant = int(entry_venta_cant.get())
        for p in inventario:
            if p['nombre'].lower() == nombre:
                if p['cantidad'] >= cant:
                    p['cantidad'] -= cant
                    # Guardar venta
                    v_list = []
                    if os.path.exists(ARCHIVO_VENTAS):
                        with open(ARCHIVO_VENTAS, "r") as f: v_list = json.load(f)
                    v_list.append({
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "pdv": archivo_actual.replace("inventario_", "").replace(".json", "").upper(),
                        "producto": p['nombre'], "cantidad": cant, "total": p['precio'] * cant
                    })
                    with open(ARCHIVO_VENTAS, "w") as f: json.dump(v_list, f, indent=4)
                    
                    guardar_datos(); actualizar_lista()
                    entry_venta_nom.delete(0, tk.END); entry_venta_cant.delete(0, tk.END)
                    messagebox.showinfo("Venta", "¡Venta registrada con éxito!")
                    return
                else:
                    messagebox.showwarning("Sin Stock", "No tienes suficiente producto.")
                    return
        messagebox.showerror("Error", "Producto no encontrado.")
    except: messagebox.showerror("Error", "Escribe un número en 'Número de venta'.")

def ventana_agregar():
    def realizar():
        try:
            inventario.append({"nombre": en.get(), "marca": em.get(), "cantidad": int(ec.get()), "precio": float(ep.get())})
            guardar_datos(); actualizar_lista(); v.destroy()
        except: messagebox.showerror("Error", "Datos inválidos")
    v = tk.Toplevel(bg="#efebe9")
    v.title("Agregar")
    tk.Label(v, text="Nombre:", bg="#efebe9").grid(row=0, column=0, padx=5, pady=5)
    en = tk.Entry(v); en.grid(row=0, column=1, padx=5)
    tk.Label(v, text="Marca:", bg="#efebe9").grid(row=1, column=0, padx=5, pady=5)
    em = tk.Entry(v); em.grid(row=1, column=1, padx=5)
    tk.Label(v, text="Stock:", bg="#efebe9").grid(row=2, column=0, padx=5, pady=5)
    ec = tk.Entry(v); ec.grid(row=2, column=1, padx=5)
    tk.Label(v, text="Precio:", bg="#efebe9").grid(row=3, column=0, padx=5, pady=5)
    ep = tk.Entry(v); ep.grid(row=3, column=1, padx=5)
    tk.Button(v, text="GUARDAR", command=realizar, bg="#4e342e", fg="white").grid(row=4, columnspan=2, pady=10)

def eliminar():
    try:
        idx = lista_vis.curselection()[0]
        if messagebox.askyesno("Confirmar", "¿Borrar este producto?"):
            inventario.pop(idx); guardar_datos(); actualizar_lista()
    except: pass

def ver_todo():
    ventana_rep = tk.Toplevel()
    ventana_rep.title("Inventario Global")
    t = tk.Text(ventana_rep, font=("Courier New", 10), padx=10, pady=10)
    t.pack(expand=True, fill='both')
    archivos = glob.glob("inventario_*.json")
    t.insert(tk.END, "ESTADO DE TODOS LOS PUNTOS\n" + "="*30 + "\n")
    for arch in archivos:
        nombre = arch.replace("inventario_", "").replace(".json", "").upper()
        t.insert(tk.END, f"\n📍 PDV: {nombre}\n")
        with open(arch, "r") as f:
            datos = json.load(f)
            for p in datos:
                t.insert(tk.END, f"- {p['nombre'][:15]:<15} | Stock: {p['cantidad']}\n")
    t.config(state=tk.DISABLED)

# --- VENTANA PRINCIPAL ---
root = tk.Tk()
root.geometry("580x850")
root.configure(bg="#3e2723")

tk.Label(root, text="SISTEMA DE IMPULSO E INVENTARIOS", font=("Impact", 18), bg="#3e2723", fg="#d7ccc8").pack(pady=15)

main = tk.Frame(root, bg="#efebe9", padx=15, pady=15)
main.pack(fill="both", expand=True, padx=20, pady=10)

# Botones Navegación
nav = tk.Frame(main, bg="#efebe9")
nav.pack(fill="x", pady=5)
tk.Button(nav, text="🔄 CAMBIAR PDV", command=seleccionar_pdv, bg="#1a73e8", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill="x", padx=2)
tk.Button(nav, text="📊 VER TODO", command=ver_todo, bg="#a1887f", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill="x", padx=2)
tk.Button(nav, text="💰 CIERRE", command=reporte_diario_pdv, bg="#2e7d32", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, expand=True, fill="x", padx=2)

lista_vis = tk.Listbox(main, width=65, height=12, font=("Arial", 10)); lista_vis.pack(pady=10)

# Botones Gestión
gest = tk.Frame(main, bg="#efebe9")
gest.pack(fill="x")
tk.Button(gest, text="+ AGREGAR", command=ventana_agregar, bg="#4e342e", fg="white").pack(side=tk.LEFT, expand=True, fill="x", padx=2)
tk.Button(gest, text="🗑️ ELIMINAR", command=eliminar, bg="#b71c1c", fg="white").pack(side=tk.LEFT, expand=True, fill="x", padx=2)

# Venta
venta = tk.LabelFrame(main, text=" REGISTRAR VENTA ", bg="#efebe9", font=("Arial", 10, "bold"))
venta.pack(pady=15, fill="x")
tk.Label(venta, text="Producto:", bg="#efebe9").grid(row=0, column=0, padx=10, pady=5)
entry_venta_nom = tk.Entry(venta, font=("Arial", 12)); entry_venta_nom.grid(row=0, column=1, padx=10)
tk.Label(venta, text="Número de venta:", bg="#efebe9").grid(row=1, column=0, padx=10, pady=5)
entry_venta_cant = tk.Entry(venta, font=("Arial", 12)); entry_venta_cant.grid(row=1, column=1, padx=10)
tk.Button(venta, text="🛒 CONFIRMAR VENTA", command=registrar_venta, bg="#ff9800", font=("Arial", 12, "bold"), height=2).grid(row=2, columnspan=2, pady=10, sticky="nsew", padx=20)

root.after(100, seleccionar_pdv)
root.mainloop()