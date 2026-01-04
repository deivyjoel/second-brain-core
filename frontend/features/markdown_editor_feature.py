import re
from typing import TypedDict, Optional, Any, Callable
import tkinter as tk
from tkinter import ttk
from frontend.core.bus import Bus

class MatchData(TypedDict):
    kind: str
    full_start: int
    full_end: int
    inner_start: int
    inner_end: int
    text: str

# ------------------
class RenderedMarkdown:
    @staticmethod
    def _find_inline_matches(raw_text: str) -> list[MatchData]:
        '''
        Find all format matches inline (bold, italic, code, strike) 
        in the given text.

        Args:
            body_text: The portion of text where to search for matches (e.g., the content 
            of a line or the body of a header).

        Returns:
            A list of dictionaries (MatchData) with the details of each match.
        '''
        
        matches: list[MatchData] = []

        for kind in INLINE_FORMATS:
            pattern = MARKDOWN_PATTERNS.get(kind)
            if not pattern: continue
                    
            pat_compiled = re.compile(pattern)
                    
            for m in pat_compiled.finditer(raw_text):
                        matches.append({
                            "kind": kind,
                            "full_start": m.start(0),  
                            "full_end": m.end(0),
                            "inner_start": m.start(1), 
                            "inner_end": m.end(1), 
                            "text": m.group(1)
                        })
        return matches
    
    @staticmethod
    def _sort_and_filter_overlaps(matches: list[MatchData]) -> list[MatchData]:
        '''
        Sort matches by start and filter out overlapping matches, 
        prioritizing the match that starts first and excluding those that start 
        before the current match ends.

        Note: This simplifies the analysis of overlaps (e.g., `**pepe~~**~~`) 
        by ignoring any match that starts within one already added.

        Args:
            matches: Unordered list of MatchData.

        Returns:
            Sorted and filtered list of MatchData.
        '''
        matches.sort(key=lambda x: x["full_start"])
        filtered: list[MatchData] = []
        cur = 0
        for mm in matches:
            if mm["full_start"] >= cur:
                filtered.append(mm)
                cur = mm["full_end"]
        return filtered

    @staticmethod
    def find_and_order_matches(raw_text: str) -> list[MatchData]:
        '''
        Main function to find and sort format matches online.

        Args:
            body_text: Text where to find the format.

        Returns:
            Sorted and filtered list of matches.
        '''
        matches = RenderedMarkdown._find_inline_matches(raw_text)
        return RenderedMarkdown._sort_and_filter_overlaps(matches)

    @staticmethod
    def build_preview_line_and_raw_to_preview_mapping(raw_text: str, matches: list[MatchData]) -> tuple[str, list[int]]:
        '''
        Processes a line of original text with syntax and generates two outputs:
        1. `preview_line`: The preview line with the formatting syntax removed.
        2. `raw_to_preview_map`: An index map relating the position of each 
        character on the original line (`raw_line`) with its position in 
        `preview_line`. Syntax positions (e.g., `**`) point 
        to the starting index of the clean text that follows.

        Args:
            raw_line: The original line of text.
            matches: The sorted and filtered list of MatchData for this line.

        Returns:
            A tuple with (preview_line: str, raw_to_preview_map: List[int]).
        '''


        preview_line_chars = []
        raw_to_preview = [-1] * (len(raw_text) + 1)
        preview_pos_line = 0

        cursor = 0  
        for mm in matches:
            fs = mm["full_start"]
            fe = mm["full_end"]
            is_ = mm["inner_start"]
            ie = mm["inner_end"]

            for k in range(cursor, fs):
                preview_line_chars.append(raw_text[k])
                raw_to_preview[k] = preview_pos_line
                preview_pos_line += 1

            for k in range(fs, is_):
                raw_to_preview[k] = preview_pos_line

            for k in range(is_, ie):
                preview_line_chars.append(raw_text[k])
                raw_to_preview[k] = preview_pos_line
                preview_pos_line += 1

            for k in range(ie, fe):
                raw_to_preview[k] = preview_pos_line

            cursor = fe

        # tail of body_text
        for k in range(cursor, len(raw_text)):
            preview_line_chars.append(raw_text[k])
            raw_to_preview[k] = preview_pos_line
            preview_pos_line += 1

        # map end-of-line index
        raw_to_preview[len(raw_text)] = preview_pos_line

        preview_line = "".join(preview_line_chars)  
        return preview_line, raw_to_preview   

    @staticmethod
    def _create_header_span(preview_text: str, header_level: int)-> Optional[tuple[str, int, int]]:
        if header_level == 0 or not preview_text:
            return None
        tag = {1:"h1",2:"h2",3:"h3",4:"h4",5:"h5",6:"h6"}[header_level]
        return (tag, 0, len(preview_text)) 

    @staticmethod
    def _get_normalized_matches_inline_matches(matches: list[MatchData], raw_body_start_idx: int) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for mm in matches:
            normalized.append({
                **mm,
                "raw_start": raw_body_start_idx + mm["inner_start"],
                "raw_end": raw_body_start_idx + mm["inner_end"],  
            })
        return normalized 

    @staticmethod
    def _create_inline_spans(normalized_matches: list[dict], raw_to_preview_map: list[int]) -> list[tuple[str, int, int]]:
        spans: list[tuple[str, int, int]] = []
        for match in normalized_matches:
            try:
                start_preview_idx = raw_to_preview_map[match["raw_start"]]
                end_preview_idx = raw_to_preview_map[match["raw_end"]]

            except IndexError:
                continue

            if end_preview_idx > start_preview_idx:
                spans.append((match["kind"], start_preview_idx, end_preview_idx))
        return spans

    @staticmethod
    def build_line_spans(
        preview_line: str, 
        matches: list[MatchData], 
        raw_to_preview_map: list[int], 
        body_start_raw_idx: int, 
        header_level: int
        ) -> list[tuple[str, int, int]]:

        spans: list[tuple[str, int, int]] = []

        header_span = RenderedMarkdown._create_header_span(preview_line, header_level)
        if header_span:
            spans.append(header_span)
        
        normalized_matches = RenderedMarkdown._get_normalized_matches_inline_matches(matches, body_start_raw_idx)
        
        inline_spans = RenderedMarkdown._create_inline_spans(normalized_matches, raw_to_preview_map)
        spans.extend(inline_spans)
        return spans
    
    @staticmethod
    def build_preview_and_maps(raw_text: str) -> tuple[str, list[list[int]], list[tuple[str, int, int]]]:
            """
            Build preview_text (markers removed) and:
            - maps: list per raw line -> list mapping raw column idx -> absolute preview idx
            - spans: list of (tagname, start_abs, end_abs) in preview absolute coordinates
            """
            preview_lines: list[str] = [] 
            raw_to_preview_maps: list[list[int]] = [] 
            absolute_spans: list[tuple[str, int, int]] = []

            abs_pos = 0 

            raw_lines = raw_text.splitlines()
            header_pattern = re.compile(MARKDOWN_PATTERNS["h_all"])

            for raw_line in raw_lines:
                #print("Abs_pos : ", abs_pos)

                header_match = header_pattern.match(raw_line)
                if header_match:
                    body_text = header_match.group(2)
                    body_start_raw_idx = header_match.start(2)
                    header_level = len(header_match.group(1)) 
                else:
                    body_text = raw_line
                    body_start_raw_idx = 0
                    header_level = 0
                #print("Body_text          : ", body_text)
                #print("Body_start_raw_idx : ", body_start_raw_idx)
                #print("Header_level       : ", header_level)

                #print("Find and order matches ... ")
                matches = RenderedMarkdown.find_and_order_matches(body_text)
                #print("Matches            : ", matches)

                #print("Build previw line and raw to preview mapping ... ")
                preview_line, raw_to_preview_line_map = RenderedMarkdown.build_preview_line_and_raw_to_preview_mapping(body_text, matches)
                #print("Preview_line           : ", preview_line)
                #print("Raw_to_preview_line_map:, ", raw_to_preview_line_map)

                #4. Agg headers
                if header_level > 0:
                    raw_to_preview_line_map = [0] * body_start_raw_idx + raw_to_preview_line_map
                #print("Agg if headers ...")
                #print("Raw_to_preview_line_map: ", raw_to_preview_line_map)
                #5. build spans
                #print("Build spans ...")
                line_spans = RenderedMarkdown.build_line_spans(
                preview_line, 
                matches, 
                raw_to_preview_line_map, # Mapeo corregido (si es encabezado) o normal (si no)
                body_start_raw_idx, 
                header_level
                )
                #print("Line Spans : ", line_spans)

                for tag, start_rel, end_rel in line_spans:
                    absolute_spans.append((tag, abs_pos + start_rel, abs_pos + end_rel))

                # save line and map (convert raw_to_preview to absolute)
                abs_map = [abs_pos + v for v in raw_to_preview_line_map]
                raw_to_preview_maps.append(abs_map)
                
                preview_lines.append(preview_line)
                abs_pos += len(preview_line) + 1

            # join lines with newline
            preview_text = "\n".join(preview_lines)
            return preview_text, raw_to_preview_maps, absolute_spans

MARKDOWN_PATTERNS = {
            "h_all": r'^(#{1,6})\s+(.*)$', 
            "bold": r'\*\*(.+?)\*\*',   
            "italic": r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', # 
            "strike": r'~~(.+?)~~',       
            "code_inline": r'`([^`\n]+?)`' 
        }
    
INLINE_FORMATS = ["code_inline", "bold", "strike", "italic"]


class MarkdownEditorFeature(ttk.Frame):
    """
    Feature: MarkdownEditor
    Contenedor (Frame) que encapsula el widget de texto y su scrollbar.
    """
    def __init__(self, master, id_note, **kwargs):
        super().__init__(master)
        self.id_note = id_note
        # Estado interno
        self.preview_mode = False
        self._markdown_text = ""
        self._markdown_cursor_position = "1.0"
        self._markdown_to_render_map = []

        self._create_widgets(kwargs)
        self._setup_tags()
        self._setup_events()
        

    def _create_widgets(self, text_kwargs):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # El widget de texto real
        params = {
            "wrap": "word",
            "font": ("Segoe UI", 11),
            "undo": True,
            "autoseparators": True,
            "relief": "flat"
        }
        params.update(text_kwargs)
        
        self.text = tk.Text(self, **params)
        self.text.grid(row=0, column=0, sticky="nsew")

        # Scrollbar integrada
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky="ns")

    def _setup_tags(self):
        t = self.text
        t.tag_configure("h1", font=("Segoe UI", 26, "bold"))
        t.tag_configure("h2", font=("Segoe UI", 20, "bold"))
        t.tag_configure("h3", font=("Segoe UI", 16, "bold"))
        t.tag_configure("h4", font=("Segoe UI", 14, "bold"))
        t.tag_configure("h5", font=("Segoe UI", 12, "bold"))
        t.tag_configure("h6", font=("Segoe UI", 10, "bold"))
        t.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        t.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        t.tag_configure("strike", overstrike=True)
        t.tag_configure("code_inline", background="#f3f3f3", font=("Consolas", 10))

    def _setup_events(self):
        self.text.bind("<Control-e>", self.toggle_preview)
        self.text.bind("<Control-E>", self.toggle_preview)

    # --- API PÚBLICA (Proxy de métodos de tk.Text) ---
    # Esto permite que el NoteEditor use .get(), .insert(), etc.

    def get(self, *args, **kwargs): 
        return self.text.get(*args, **kwargs)
    def insert(self, *args, **kwargs): 
        return self.text.insert(*args, **kwargs)
    def delete(self, *args, **kwargs): 
        return self.text.delete(*args, **kwargs)
    def edit_modified(self, *args, **kwargs): 
        return self.text.edit_modified(*args, **kwargs)
    def edit_reset(self, *args, **kwargs): 
        return self.text.edit_reset(*args, **kwargs)
    def mark_set(self, *args, **kwargs): 
        return self.text.mark_set(*args, **kwargs)

    # --- LÓGICA DE PREVIEW ---

    def toggle_preview(self, event=None) -> str:
        """Switches between Markdown editing mode and preview mode."""
        if not self.preview_mode:
            self._enter_preview_mode()
            Bus.emit("ACTIVE_MARKDOWN", is_active=True, id_note= self.id_note)
        else:
            self._restore_markdown_mode()
            Bus.emit("ACTIVE_MARKDOWN", is_active=False, id_note = self.id_note)
        return "break"

    def _enter_preview_mode(self):
        # Obtener el texto sin formato actual
        self._markdown_text = self.text.get("1.0", "end-1c")
        # Obtener la pocición actual del cursor
        self._markdown_cursor_position = self.text.index("insert")

        # Construir el texto de vista previa y los mapas
        preview_text, maps, spans = self._build_preview_and_maps(self._markdown_text)
        self._markdown_to_render_map = maps

        # Borramos el texto completo actual
        self.text.delete("1.0", "end")

        # Insertamos el nuevo texto limpio
        self.text.insert("1.0", preview_text)
        
        # Removemos los formatos
        for tag in ("h1","h2","h3","h4","h5","h6","bold","italic","strike","code_inline"):
            self.text.tag_remove(tag, "1.0", "end")

        # Aplicamos los formatos
        for tagname, start_abs, end_abs in spans:
            if end_abs > start_abs:
                try:
                    self.text.tag_add(tagname, f"1.0+{start_abs}c", f"1.0+{end_abs}c")
                except tk.TclError: 
                    pass

        try:
            pr_pos = self._map_raw_index_to_preview(self._markdown_cursor_position)
            self.text.mark_set("insert", f"1.0+{pr_pos}c")
            self.text.see("insert")
        except: 
            pass

        self.preview_mode = True

    def _restore_markdown_mode(self):
        """Restore the original Markdown text and cursor."""
        self.text.delete("1.0", "end")
        self.text.insert("1.0", self._markdown_text)
        self.preview_mode = False
        try:
            self.text.mark_set("insert", self._markdown_cursor_position)
            self.text.see("insert")
        except: pass

    # --- ALGORITMO DE PARSEO (Privado) ---
    def _build_preview_and_maps(self, raw_text: str):
        return RenderedMarkdown.build_preview_and_maps(raw_text)

    def _map_raw_index_to_preview(self, raw_index):
        """
        Map a tk index in raw text like '3.5' to an
        absolute preview char index using self._raw2preview_maps.
        Returns and integer absolute char index (0-based)
        """

        if not self._markdown_to_render_map: 
            return 0
        line_str, col_str = raw_index.split(".")
        line, col = int(line_str) - 1, int(col_str)
        if line < 0: 
            return 0
        if line >= len(self._markdown_to_render_map): 
            return self._markdown_to_render_map[-1][-1]
        amap = self._markdown_to_render_map[line]
        if col < 0:
            col = 0
        if col >= len(amap):
            return amap[-1]
        return amap[col]

    def get_markdown(self) -> str:
        """Devuelve el Markdown fuente, sin importar el modo."""
        if self.preview_mode:
            return self._markdown_text
        return self.text.get("1.0", "end-1c")
