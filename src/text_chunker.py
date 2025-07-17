import re
from typing import List, Tuple, Optional
from .logger import setup_logger

logger = setup_logger("text_chunker")

class TextChunker:
    """Zerlegt Texte in einzelne Teile (Chunks)."""

    # Der bisherige Ablauf:
    # 1. Text wird zeilenweise eingelesen.
    # 2. Jede Zeile wird, falls nötig, an Wortgrenzen in den aktuellen
    #    Chunk eingefügt.
    # 3. Überschreitet eine Zeile die maximale Chunk-Größe, wird sie
    #    selbst an Wortgrenzen aufgeteilt.
    # 4. Fertige Chunks werden in einer Liste gesammelt und zurückgegeben.
    
    def __init__(self, max_chunk_size: int = 5000):
        """
        Initialisiert den TextChunker.
        
        Args:
            max_chunk_size: Maximale Anzahl von Zeichen pro Chunk
        """
        # Standardmäßig ist die Chunk-Größe fest auf 5000 Zeichen gesetzt.
        # Dieser Wert wird nun über die neue GUI dynamisch angepasst.
        self.max_chunk_size = max_chunk_size
        logger.info(f"TextChunker initialisiert mit max_chunk_size={max_chunk_size}")
    
    def split_text(self, text: str) -> List[str]:
        """
        Teilt einen Text in Chunks auf, ohne Wörter zu trennen.
        
        Args:
            text: Der zu teilende Text
            
        Returns:
            Liste von Text-Chunks
        """
        if not text:
            return []
        
        chunks = []
        current_chunk = ""
        
        # Text in Zeilen aufteilen für bessere Kontrolle
        lines = text.split('\n')
        
        for line in lines:
            # Prüfen ob die Zeile selbst zu lang ist
            if len(line) > self.max_chunk_size:
                # Aktuelle Chunk speichern, falls vorhanden
                if current_chunk:
                    chunks.append(current_chunk.rstrip())
                    current_chunk = ""
                
                # Lange Zeile in Wörter aufteilen
                words = line.split()
                for word in words:
                    if len(current_chunk) + len(word) + 1 > self.max_chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk.rstrip())
                        current_chunk = word + " "
                    else:
                        current_chunk += word + " "
                current_chunk = current_chunk.rstrip() + "\n"
            else:
                # Prüfen ob Zeile in aktuellen Chunk passt
                if len(current_chunk) + len(line) + 1 > self.max_chunk_size:
                    chunks.append(current_chunk.rstrip())
                    current_chunk = line + "\n"
                else:
                    current_chunk += line + "\n"
        
        # Letzten Chunk hinzufügen
        if current_chunk:
            chunks.append(current_chunk.rstrip())
        
        logger.info(f"Text aufgeteilt in {len(chunks)} Chunks")
        return chunks
    
    def detect_speaker(self, line: str) -> Optional[Tuple[str, str]]:
        """
        Erkennt Sprecher in einer Chat-Zeile.
        
        Args:
            line: Eine Zeile aus dem Chat
            
        Returns:
            Tuple (Sprecher, Nachricht) oder None
        """
        # WhatsApp Format: "DD.MM.YY, HH:MM - Name: Nachricht"
        whatsapp_pattern = r'^\d{1,2}\.\d{1,2}\.\d{2,4},\s*\d{1,2}:\d{2}\s*-\s*([^:]+):\s*(.+)$'
        match = re.match(whatsapp_pattern, line)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        # Einfaches Format: "Name: Nachricht"
        simple_pattern = r'^([^:]+):\s*(.+)$'
        match = re.match(simple_pattern, line)
        if match and len(match.group(1)) < 50:  # Name sollte nicht zu lang sein
            return match.group(1).strip(), match.group(2).strip()
        
        return None
    
    def format_with_speakers(self, text: str) -> str:
        """
        Formatiert Text mit erkannten Sprechern.
        
        Args:
            text: Der zu formatierende Text
            
        Returns:
            Formatierter Text mit Sprechern pro Zeile
        """
        lines = text.split('\n')
        formatted_lines = []
        current_speaker = None
        
        for line in lines:
            speaker_info = self.detect_speaker(line)
            if speaker_info:
                speaker, message = speaker_info
                if speaker != current_speaker:
                    formatted_lines.append(f"\n[{speaker}]")
                    current_speaker = speaker
                formatted_lines.append(message)
            else:
                # Zeile ohne erkannten Sprecher
                if line.strip():
                    formatted_lines.append(line)
        
        return '\n'.join(formatted_lines) 