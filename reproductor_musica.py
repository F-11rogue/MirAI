"""
Reproductor de Música en Python
================================
Un reproductor de música simple con interfaz gráfica usando tkinter y pygame.

Características:
- Reproducir, pausar, detener música
- Control de volumen
- Siguiente/Anterior canción
- Gestión de lista de reproducción
- Soporte para archivos MP3 y WAV
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

try:
    import pygame
except ImportError:
    raise ImportError(
        "pygame es necesario para ejecutar este reproductor. "
        "Instálalo con: pip install pygame"
    )


class ReproductorMusica:
    """Clase principal del reproductor de música."""

    def __init__(self, root: tk.Tk):
        """
        Inicializa el reproductor de música.
        
        Args:
            root: Ventana principal de tkinter
        """
        self.root = root
        self.root.title("🎵 Reproductor de Música")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        self.root.configure(bg="#2b2b2b")

        # Inicializar pygame mixer para reproducción de audio
        pygame.mixer.init()

        # Variables de estado
        self.lista_reproduccion: List[str] = []
        self.cancion_actual: int = -1
        self.esta_reproduciendo: bool = False
        self.esta_pausado: bool = False
        self.volumen: float = 0.7

        # Configurar la interfaz
        self._crear_interfaz()

        # Configurar el volumen inicial
        pygame.mixer.music.set_volume(self.volumen)

        # Manejar el cierre de la ventana
        self.root.protocol("WM_DELETE_WINDOW", self._al_cerrar)

    def _crear_interfaz(self) -> None:
        """Crea todos los elementos de la interfaz gráfica."""
        # Frame principal
        frame_principal = tk.Frame(self.root, bg="#2b2b2b")
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Título
        titulo = tk.Label(
            frame_principal,
            text="🎵 Reproductor de Música",
            font=("Helvetica", 18, "bold"),
            bg="#2b2b2b",
            fg="#ffffff"
        )
        titulo.pack(pady=10)

        # Frame para la lista de reproducción
        frame_lista = tk.Frame(frame_principal, bg="#2b2b2b")
        frame_lista.pack(fill=tk.BOTH, expand=True, pady=10)

        # Scrollbar para la lista
        scrollbar = tk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Lista de canciones
        self.lista_canciones = tk.Listbox(
            frame_lista,
            bg="#3c3c3c",
            fg="#ffffff",
            selectbackground="#4a90d9",
            selectforeground="#ffffff",
            font=("Helvetica", 10),
            yscrollcommand=scrollbar.set,
            activestyle="dotbox"
        )
        self.lista_canciones.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_canciones.yview)

        # Etiqueta de canción actual
        self.etiqueta_cancion = tk.Label(
            frame_principal,
            text="Ninguna canción seleccionada",
            font=("Helvetica", 10),
            bg="#2b2b2b",
            fg="#aaaaaa",
            wraplength=450
        )
        self.etiqueta_cancion.pack(pady=5)

        # Frame para controles de reproducción
        frame_controles = tk.Frame(frame_principal, bg="#2b2b2b")
        frame_controles.pack(pady=10)

        # Estilo de botones
        estilo_boton = {
            "font": ("Helvetica", 12),
            "width": 3,
            "bg": "#4a4a4a",
            "fg": "#ffffff",
            "activebackground": "#5a5a5a",
            "activeforeground": "#ffffff",
            "relief": tk.FLAT,
            "cursor": "hand2"
        }

        # Botones de control
        btn_anterior = tk.Button(
            frame_controles,
            text="⏮",
            command=self.anterior,
            **estilo_boton
        )
        btn_anterior.pack(side=tk.LEFT, padx=5)

        btn_reproducir = tk.Button(
            frame_controles,
            text="▶",
            command=self.reproducir,
            **estilo_boton
        )
        btn_reproducir.pack(side=tk.LEFT, padx=5)

        btn_pausar = tk.Button(
            frame_controles,
            text="⏸",
            command=self.pausar,
            **estilo_boton
        )
        btn_pausar.pack(side=tk.LEFT, padx=5)

        btn_detener = tk.Button(
            frame_controles,
            text="⏹",
            command=self.detener,
            **estilo_boton
        )
        btn_detener.pack(side=tk.LEFT, padx=5)

        btn_siguiente = tk.Button(
            frame_controles,
            text="⏭",
            command=self.siguiente,
            **estilo_boton
        )
        btn_siguiente.pack(side=tk.LEFT, padx=5)

        # Frame para control de volumen
        frame_volumen = tk.Frame(frame_principal, bg="#2b2b2b")
        frame_volumen.pack(pady=10, fill=tk.X)

        etiqueta_volumen = tk.Label(
            frame_volumen,
            text="🔊 Volumen:",
            font=("Helvetica", 10),
            bg="#2b2b2b",
            fg="#ffffff"
        )
        etiqueta_volumen.pack(side=tk.LEFT, padx=5)

        self.slider_volumen = ttk.Scale(
            frame_volumen,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            command=self._cambiar_volumen
        )
        self.slider_volumen.set(70)
        self.slider_volumen.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.etiqueta_porcentaje = tk.Label(
            frame_volumen,
            text="70%",
            font=("Helvetica", 10),
            bg="#2b2b2b",
            fg="#ffffff",
            width=5
        )
        self.etiqueta_porcentaje.pack(side=tk.LEFT)

        # Frame para botones de gestión de lista
        frame_gestion = tk.Frame(frame_principal, bg="#2b2b2b")
        frame_gestion.pack(pady=10)

        estilo_boton_gestion = {
            "font": ("Helvetica", 9),
            "bg": "#4a90d9",
            "fg": "#ffffff",
            "activebackground": "#357abd",
            "activeforeground": "#ffffff",
            "relief": tk.FLAT,
            "cursor": "hand2",
            "padx": 10,
            "pady": 5
        }

        btn_agregar = tk.Button(
            frame_gestion,
            text="➕ Agregar",
            command=self.agregar_canciones,
            **estilo_boton_gestion
        )
        btn_agregar.pack(side=tk.LEFT, padx=5)

        btn_eliminar = tk.Button(
            frame_gestion,
            text="➖ Eliminar",
            command=self.eliminar_cancion,
            **estilo_boton_gestion
        )
        btn_eliminar.pack(side=tk.LEFT, padx=5)

        btn_limpiar = tk.Button(
            frame_gestion,
            text="🗑 Limpiar",
            command=self.limpiar_lista,
            **estilo_boton_gestion
        )
        btn_limpiar.pack(side=tk.LEFT, padx=5)

        # Vincular doble clic para reproducir
        self.lista_canciones.bind("<Double-1>", self._reproducir_seleccion)

    def agregar_canciones(self) -> None:
        """Abre un diálogo para seleccionar y agregar canciones a la lista."""
        archivos = filedialog.askopenfilenames(
            title="Seleccionar canciones",
            filetypes=[
                ("Archivos de audio", "*.mp3 *.wav *.ogg"),
                ("MP3", "*.mp3"),
                ("WAV", "*.wav"),
                ("OGG", "*.ogg"),
                ("Todos los archivos", "*.*")
            ]
        )

        for archivo in archivos:
            if archivo not in self.lista_reproduccion:
                self.lista_reproduccion.append(archivo)
                nombre = os.path.basename(archivo)
                self.lista_canciones.insert(tk.END, nombre)

    def eliminar_cancion(self) -> None:
        """Elimina la canción seleccionada de la lista."""
        seleccion = self.lista_canciones.curselection()
        if seleccion:
            indice = seleccion[0]
            self.lista_canciones.delete(indice)
            del self.lista_reproduccion[indice]

            # Ajustar el índice de la canción actual si es necesario
            if indice == self.cancion_actual:
                self.detener()
                self.cancion_actual = -1
            elif indice < self.cancion_actual:
                self.cancion_actual -= 1

    def limpiar_lista(self) -> None:
        """Limpia toda la lista de reproducción."""
        if self.lista_reproduccion:
            if messagebox.askyesno(
                "Confirmar",
                "¿Estás seguro de que deseas limpiar la lista?"
            ):
                self.detener()
                self.lista_canciones.delete(0, tk.END)
                self.lista_reproduccion.clear()
                self.cancion_actual = -1
                self.etiqueta_cancion.config(text="Ninguna canción seleccionada")

    def reproducir(self) -> None:
        """Reproduce la canción seleccionada o continúa desde la pausa."""
        if self.esta_pausado:
            pygame.mixer.music.unpause()
            self.esta_pausado = False
            self.esta_reproduciendo = True
            return

        seleccion = self.lista_canciones.curselection()
        if seleccion:
            indice = seleccion[0]
            self._reproducir_indice(indice)
        elif self.lista_reproduccion and self.cancion_actual == -1:
            self._reproducir_indice(0)
            self.lista_canciones.selection_set(0)

    def _reproducir_indice(self, indice: int) -> None:
        """
        Reproduce la canción en el índice especificado.
        
        Args:
            indice: Índice de la canción en la lista
        """
        if 0 <= indice < len(self.lista_reproduccion):
            try:
                ruta = self.lista_reproduccion[indice]
                pygame.mixer.music.load(ruta)
                pygame.mixer.music.play()
                self.cancion_actual = indice
                self.esta_reproduciendo = True
                self.esta_pausado = False

                nombre = os.path.basename(ruta)
                self.etiqueta_cancion.config(text=f"🎶 Reproduciendo: {nombre}")

                # Resaltar la canción actual
                self.lista_canciones.selection_clear(0, tk.END)
                self.lista_canciones.selection_set(indice)
                self.lista_canciones.see(indice)

            except pygame.error as e:
                messagebox.showerror(
                    "Error",
                    f"No se pudo reproducir el archivo:\n{e}"
                )

    def _reproducir_seleccion(self, event) -> None:
        """Maneja el doble clic para reproducir una canción."""
        seleccion = self.lista_canciones.curselection()
        if seleccion:
            self._reproducir_indice(seleccion[0])

    def pausar(self) -> None:
        """Pausa o reanuda la reproducción actual."""
        if self.esta_reproduciendo and not self.esta_pausado:
            pygame.mixer.music.pause()
            self.esta_pausado = True
            self.esta_reproduciendo = False
        elif self.esta_pausado:
            pygame.mixer.music.unpause()
            self.esta_pausado = False
            self.esta_reproduciendo = True

    def detener(self) -> None:
        """Detiene la reproducción actual."""
        pygame.mixer.music.stop()
        self.esta_reproduciendo = False
        self.esta_pausado = False
        self.etiqueta_cancion.config(text="Reproducción detenida")

    def siguiente(self) -> None:
        """Reproduce la siguiente canción en la lista."""
        if self.lista_reproduccion:
            nuevo_indice = (self.cancion_actual + 1) % len(self.lista_reproduccion)
            self._reproducir_indice(nuevo_indice)

    def anterior(self) -> None:
        """Reproduce la canción anterior en la lista."""
        if self.lista_reproduccion:
            nuevo_indice = (self.cancion_actual - 1) % len(self.lista_reproduccion)
            self._reproducir_indice(nuevo_indice)

    def _cambiar_volumen(self, valor: str) -> None:
        """
        Cambia el volumen de reproducción.
        
        Args:
            valor: Valor del slider (0-100)
        """
        self.volumen = float(valor) / 100
        pygame.mixer.music.set_volume(self.volumen)
        self.etiqueta_porcentaje.config(text=f"{int(float(valor))}%")

    def _al_cerrar(self) -> None:
        """Maneja el cierre limpio de la aplicación."""
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()


def main() -> None:
    """Función principal para ejecutar el reproductor de música."""
    root = tk.Tk()
    reproductor = ReproductorMusica(root)
    root.mainloop()


if __name__ == "__main__":
    main()
