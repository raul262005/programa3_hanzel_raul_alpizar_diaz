# Este es la primera version del proyecto

import tkinter as tk
from tkinter import messagebox

def jugar():
    messagebox.showinfo("Jugar", "Version de prueba.")

def configurar():
    messagebox.showinfo("Configurar", "Version de prueba.")

def acerca_de():
    messagebox.showinfo("Acerca de", "Version de prueba.")

def ayuda():
    messagebox.showinfo("Ayuda", "Version de prueba.")

def salir():
    ventana.destroy()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Kakuro")
ventana.geometry("300x300")  # Tamaño de la ventana

# Crear y colocar los botones verticalmente
tk.Button(ventana, text="Jugar", command=jugar, height=2, width=20).pack(pady=5)
tk.Button(ventana, text="Configurar", command=configurar, height=2, width=20).pack(pady=5)
tk.Button(ventana, text="Acerca de", command=acerca_de, height=2, width=20).pack(pady=5)
tk.Button(ventana, text="Ayuda", command=ayuda, height=2, width=20).pack(pady=5)
tk.Button(ventana, text="Salir", command=salir, height=2, width=20).pack(pady=5)

# Ejecutar la ventana
ventana.mainloop()
