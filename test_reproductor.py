"""
Tests para el Reproductor de Música
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch, MagicMock

# Configure headless environment for tests
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'


class TestReproductorMusica(unittest.TestCase):
    """Tests para la clase ReproductorMusica."""

    @patch('reproductor_musica.pygame.mixer')
    @patch('reproductor_musica.tk.Tk')
    def test_inicializacion(self, mock_tk, mock_mixer):
        """Verifica que el reproductor se inicialice correctamente."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        from reproductor_musica import ReproductorMusica
        
        reproductor = ReproductorMusica(mock_root)
        
        # Verificar estado inicial
        self.assertEqual(reproductor.lista_reproduccion, [])
        self.assertEqual(reproductor.cancion_actual, -1)
        self.assertFalse(reproductor.esta_reproduciendo)
        self.assertFalse(reproductor.esta_pausado)
        self.assertEqual(reproductor.volumen, 0.7)

    @patch('reproductor_musica.pygame.mixer')
    @patch('reproductor_musica.tk.Tk')
    def test_cambiar_volumen(self, mock_tk, mock_mixer):
        """Verifica que el volumen se cambie correctamente."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        from reproductor_musica import ReproductorMusica
        
        reproductor = ReproductorMusica(mock_root)
        
        # Cambiar volumen a 50%
        reproductor._cambiar_volumen("50")
        
        self.assertEqual(reproductor.volumen, 0.5)
        mock_mixer.music.set_volume.assert_called_with(0.5)

    @patch('reproductor_musica.pygame.mixer')
    @patch('reproductor_musica.tk.Tk')
    def test_detener(self, mock_tk, mock_mixer):
        """Verifica que detener funcione correctamente."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        from reproductor_musica import ReproductorMusica
        
        reproductor = ReproductorMusica(mock_root)
        reproductor.esta_reproduciendo = True
        
        reproductor.detener()
        
        self.assertFalse(reproductor.esta_reproduciendo)
        self.assertFalse(reproductor.esta_pausado)
        mock_mixer.music.stop.assert_called()

    @patch('reproductor_musica.pygame.mixer')
    @patch('reproductor_musica.tk.Tk')
    def test_pausar_sin_reproduccion(self, mock_tk, mock_mixer):
        """Verifica que pausar no haga nada si no hay reproducción."""
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        
        from reproductor_musica import ReproductorMusica
        
        reproductor = ReproductorMusica(mock_root)
        reproductor.esta_reproduciendo = False
        
        reproductor.pausar()
        
        # No debería haber llamado a pause
        mock_mixer.music.pause.assert_not_called()


class TestImports(unittest.TestCase):
    """Tests para verificar que las importaciones funcionan."""

    def test_import_pygame(self):
        """Verifica que pygame se puede importar."""
        import pygame
        self.assertIsNotNone(pygame)

    def test_import_tkinter(self):
        """Verifica que tkinter se puede importar."""
        import tkinter
        self.assertIsNotNone(tkinter)

    def test_import_reproductor(self):
        """Verifica que el módulo reproductor se puede importar."""
        from reproductor_musica import ReproductorMusica, main
        self.assertIsNotNone(ReproductorMusica)
        self.assertIsNotNone(main)


if __name__ == '__main__':
    unittest.main()
