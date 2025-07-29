from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk
import threading
import time

# =============================================================================
# BASE AST NODE
# =============================================================================

class ASTNode:
    pass

# =============================================================================
# BASIC AST NODES
# =============================================================================

@dataclass
class NumberNode(ASTNode):
    value: float

@dataclass
class StringNode(ASTNode):
    value: str

@dataclass
class BooleanNode(ASTNode):
    value: bool

@dataclass
class NullNode(ASTNode):
    pass

@dataclass
class IdentifierNode(ASTNode):
    name: str

@dataclass
class BinaryOpNode(ASTNode):
    left: ASTNode
    operator: str
    right: ASTNode

@dataclass
class AssignmentNode(ASTNode):
    name: str
    value: ASTNode

@dataclass
class VariableDeclarationNode(ASTNode):
    name: str
    value: Optional[ASTNode] = None

@dataclass
class FunctionDefNode(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]

@dataclass
class FunctionCallNode(ASTNode):
    name: str
    args: List[ASTNode]

@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    then_branch: List[ASTNode]
    else_branch: Optional[List[ASTNode]] = None

@dataclass
class LoopNode(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class ReturnNode(ASTNode):
    value: Optional[ASTNode] = None

@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]

# =============================================================================
# 🔥 ENHANCED AST NODES FOR ADVANCED FEATURES
# =============================================================================

@dataclass
class ArrayNode(ASTNode):
    """Array literal: [1, 2, 3]"""
    elements: List[ASTNode]

@dataclass
class PropertyAccessNode(ASTNode):
    """Property access: object.property"""
    object: ASTNode
    property: str

@dataclass
class MethodCallNode(ASTNode):
    """Method call: object.method(args)"""
    object: ASTNode
    method: str
    args: List[ASTNode]

@dataclass
class YantraDeclarationNode(ASTNode):
    """GUI element creation with properties"""
    name: str
    element_type: str
    properties: Dict[str, ASTNode]

@dataclass
class ShaktiDeclarationNode(ASTNode):
    """Power expression for complex operations"""
    name: str
    expression_type: str
    properties: Dict[str, ASTNode]

@dataclass
class SutraDeclarationNode(ASTNode):
    """Function composition chain"""
    name: str
    functions: List[ASTNode]

@dataclass
class RagaDeclarationNode(ASTNode):
    """Data flow pattern"""
    name: str
    source: ASTNode
    transformations: List[ASTNode]

@dataclass
class MandalDeclarationNode(ASTNode):
    """Circular data structure"""
    name: str
    elements: List[ASTNode]

@dataclass
class SevaDefinitionNode(ASTNode):
    """Service/API definition"""
    name: str
    params: List[str]
    body: List[ASTNode]

# =============================================================================
# 🔥 MANTRA RUNTIME CLASSES
# =============================================================================

class MantraArray:
    """Enhanced array with Sanskrit methods"""
    def __init__(self, elements):
        self.elements = list(elements)
    
    def pratham(self):
        """First element (pratham = first)"""
        return self.elements[0] if self.elements else None
    
    def antim(self):
        """Last element (antim = last)"""
        return self.elements[-1] if self.elements else None
    
    def madhya(self):
        """Middle element (madhya = middle)"""
        if not self.elements:
            return None
        return self.elements[len(self.elements) // 2]
    
    def lambh(self):
        """Length (lambh = length)"""
        return len(self.elements)
    
    def yog(self, item):
        """Add item (yog = add)"""
        self.elements.append(item)
        return self
    
    def nikaal(self, index=None):
        """Remove item (nikaal = remove)"""
        if index is None:
            return self.elements.pop() if self.elements else None
        return self.elements.pop(index) if 0 <= index < len(self.elements) else None
    
    def __str__(self):
        return f"[{', '.join(str(e) for e in self.elements)}]"
    
    def __repr__(self):
        return self.__str__()

# =============================================================================
# YANTRA (GUI) SYSTEM
# =============================================================================

class YantraWidget:
    """Base class for all Yantra GUI widgets"""
    def __init__(self, widget_type: str, properties: Dict[str, Any]):
        self.widget_type = widget_type
        self.properties = properties
        self.tk_widget = None
        self.event_handlers = {}
    
    def create_widget(self, parent):
        """Create the actual tkinter widget"""
        if self.widget_type == "window":
            return self.create_window()
        elif self.widget_type == "label":
            return self.create_label(parent)
        elif self.widget_type == "button":
            return self.create_button(parent)
        elif self.widget_type == "entry":
            return self.create_entry(parent)
        elif self.widget_type == "text":
            return self.create_text(parent)
        elif self.widget_type == "frame":
            return self.create_frame(parent)
        elif self.widget_type == "menu":
            return self.create_menu(parent)
        else:
            raise ValueError(f"Unknown widget type: {self.widget_type}")
    
    def create_window(self):
        """Create a window (top-level)"""
        window = tk.Tk()
        window.title(self.properties.get('title', 'Mantra Application'))
        
        # Set size
        width = int(self.properties.get('width', 400))
        height = int(self.properties.get('height', 300))
        window.geometry(f"{width}x{height}")
        
        # Set other properties
        if 'resizable' in self.properties:
            resizable = self.properties['resizable']
            if isinstance(resizable, bool):
                window.resizable(resizable, resizable)
        
        if 'background' in self.properties:
            window.configure(bg=self.properties['background'])
        
        self.tk_widget = window
        return window
    
    def create_label(self, parent):
        """Create a label widget"""
        label = tk.Label(parent)
        
        # Set text
        if 'text' in self.properties:
            label.config(text=self.properties['text'])
        
        # Set font
        if 'font' in self.properties:
            label.config(font=self.properties['font'])
        
        # Set colors
        if 'color' in self.properties:
            label.config(fg=self.properties['color'])
        if 'background' in self.properties:
            label.config(bg=self.properties['background'])
        
        # Pack with options
        pack_options = {}
        if 'padding' in self.properties:
            pack_options['pady'] = self.properties['padding']
        
        label.pack(**pack_options)
        self.tk_widget = label
        return label
    
    def create_button(self, parent):
        """Create a button widget"""
        def button_clicked():
            if 'action' in self.properties:
                action = self.properties['action']
                if callable(action):
                    action()
                else:
                    print(f"Button '{self.properties.get('text', 'Button')}' clicked!")
        
        button = tk.Button(parent, command=button_clicked)
        
        # Set properties
        if 'text' in self.properties:
            button.config(text=self.properties['text'])
        
        if 'width' in self.properties:
            button.config(width=int(self.properties['width']) // 10)
        
        if 'height' in self.properties:
            button.config(height=int(self.properties['height']) // 20)
        
        if 'font' in self.properties:
            button.config(font=self.properties['font'])
        
        if 'color' in self.properties:
            button.config(fg=self.properties['color'])
        
        if 'background' in self.properties:
            button.config(bg=self.properties['background'])
        
        # Pack the button
        pack_options = {'pady': 5}
        if 'padding' in self.properties:
            pack_options['pady'] = self.properties['padding']
        
        button.pack(**pack_options)
        self.tk_widget = button
        return button
    
    def create_entry(self, parent):
        """Create an entry (text input) widget"""
        entry = tk.Entry(parent)
        
        # Set properties
        if 'width' in self.properties:
            entry.config(width=int(self.properties['width']) // 10)
        
        if 'font' in self.properties:
            entry.config(font=self.properties['font'])
        
        if 'placeholder' in self.properties:
            placeholder = self.properties['placeholder']
            entry.insert(0, placeholder)
            entry.config(fg='gray')
            
            def on_focus_in(event):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.config(fg='black')
            
            def on_focus_out(event):
                if entry.get() == '':
                    entry.insert(0, placeholder)
                    entry.config(fg='gray')
            
            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)
        
        # Pack the entry
        pack_options = {'pady': 5}
        if 'padding' in self.properties:
            pack_options['pady'] = self.properties['padding']
        
        entry.pack(**pack_options)
        self.tk_widget = entry
        return entry
    
    def create_text(self, parent):
        """Create a text widget for multi-line input"""
        text = tk.Text(parent)
        
        # Set properties
        if 'width' in self.properties:
            text.config(width=int(self.properties['width']) // 10)
        
        if 'height' in self.properties:
            text.config(height=int(self.properties['height']) // 20)
        
        if 'font' in self.properties:
            text.config(font=self.properties['font'])
        
        # Pack the text widget
        pack_options = {'pady': 5}
        text.pack(**pack_options)
        self.tk_widget = text
        return text
    
    def create_frame(self, parent):
        """Create a frame container"""
        frame = tk.Frame(parent)
        
        # Set properties
        if 'background' in self.properties:
            frame.config(bg=self.properties['background'])
        
        if 'border' in self.properties:
            frame.config(relief='solid', borderwidth=1)
        
        # Pack the frame
        pack_options = {'pady': 5, 'fill': 'x'}
        frame.pack(**pack_options)
        self.tk_widget = frame
        return frame
    
    def create_menu(self, parent):
        """Create a menu"""
        menu = tk.Menu(parent)
        
        # Add menu items if specified
        if 'items' in self.properties:
            for item in self.properties['items']:
                if isinstance(item, str):
                    menu.add_command(label=item)
                elif isinstance(item, dict):
                    menu.add_command(label=item.get('text', 'Item'), 
                                   command=item.get('action', lambda: None))
        
        self.tk_widget = menu
        return menu

class YantraApplication:
    """Main application manager for Yantra GUI"""
    def __init__(self):
        self.widgets = []
        self.main_window = None
        self.is_running = False
    
    def add_widget(self, widget: YantraWidget):
        """Add a widget to the application"""
        self.widgets.append(widget)
    
    def create_window(self, properties: Dict[str, Any]):
        """Create the main application window"""
        window_widget = YantraWidget("window", properties)
        self.main_window = window_widget.create_widget(None)
        return self.main_window
    
    def run(self):
        """Run the GUI application"""
        if not self.main_window:
            # Create default window if none exists
            self.main_window = self.create_window({
                'title': 'Mantra Application',
                'width': 400,
                'height': 300
            })
        
        # Create all widgets
        for widget in self.widgets:
            if widget.widget_type != "window":
                widget.create_widget(self.main_window)
        
        # Add a default close handler
        def on_closing():
            self.is_running = False
            self.main_window.destroy()
        
        self.main_window.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start the GUI
        self.is_running = True
        self.main_window.mainloop()
        
        return "Yantra application started"

# =============================================================================
# SHAKTI (POWER EXPRESSION) SYSTEM
# =============================================================================

class ShaktiProcessor:
    """Processor for Shakti power expressions"""
    
    @staticmethod
    def process_web_server(properties: Dict[str, Any]):
        """Create a simple web server"""
        port = properties.get('port', 8000)
        routes = properties.get('routes', [])
        
        try:
            import http.server
            import socketserver
            
            class MantraHTTPHandler(http.server.SimpleHTTPRequestHandler):
                def do_GET(self):
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html; charset=utf-8')
                    self.end_headers()
                    
                    html = f"""
                    <html>
                    <head>
                        <title>Mantra Web Server</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; padding: 20px; }}
                            h1 {{ color: #FF6B35; }}
                            .sanskrit {{ font-style: italic; color: #4A5568; }}
                        </style>
                    </head>
                    <body>
                        <h1>🕉️ Mantra Web Server</h1>
                        <p>Welcome to the <span class="sanskrit">Shakti</span> powered web server!</p>
                        <p>Running on port: {port}</p>
                        <p>Routes: {', '.join(routes) if routes else 'None defined'}</p>
                        <hr>
                        <p><em>Powered by Mantra Programming Language</em></p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
            
            def run_server():
                with socketserver.TCPServer(("", port), MantraHTTPHandler) as httpd:
                    print(f"🌐 Shakti web server running at http://localhost:{port}")
                    httpd.serve_forever()
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            return f"Web server started on http://localhost:{port}"
        
        except Exception as e:
            return f"Web server error: {e}"
    
    @staticmethod
    def process_database(properties: Dict[str, Any]):
        """Handle database operations"""
        db_type = properties.get('type', 'memory')
        
        if db_type == 'memory':
            # Simple in-memory database
            return MantraDatabase()
        
        return f"Database type '{db_type}' created"
    
    @staticmethod
    def process_file_operations(properties: Dict[str, Any]):
        """Handle file operations"""
        operation = properties.get('operation', 'read')
        filename = properties.get('file', 'mantra_file.txt')
        content = properties.get('content', '')
        
        try:
            if operation == 'read':
                with open(filename, 'r', encoding='utf-8') as f:
                    data = f.read()
                return data
            
            elif operation == 'write':
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(str(content))
                return f"Written to {filename}"
            
            elif operation == 'append':
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(str(content))
                return f"Appended to {filename}"
            
        except Exception as e:
            return f"File operation error: {e}"

class MantraDatabase:
    """Simple in-memory database"""
    def __init__(self):
        self.data = {}
    
    def set(self, key, value):
        self.data[key] = value
        return value
    
    def get(self, key):
        return self.data.get(key)
    
    def delete(self, key):
        if key in self.data:
            del self.data[key]
            return True
        return False
    
    def keys(self):
        return list(self.data.keys())

# =============================================================================
# SUTRA (FUNCTION COMPOSITION) SYSTEM
# =============================================================================

class SutraComposer:
    """Function composition system"""
    
    @staticmethod
    def compose(*functions):
        """Compose multiple functions into one"""
        def composed_function(x):
            result = x
            for func in reversed(functions):  # Right to left composition
                if callable(func):
                    result = func(result)
            return result
        
        return composed_function

# =============================================================================
# RAGA (DATA FLOW) SYSTEM
# =============================================================================

class RagaProcessor:
    """Data flow processing system"""
    
    @staticmethod
    def process_flow(data, transformations):
        """Process data through a series of transformations"""
        result = data
        for transform in transformations:
            if callable(transform):
                result = transform(result)
        return result

# =============================================================================
# MANDAL (CIRCULAR DATA) SYSTEM
# =============================================================================

class MandalStructure:
    """Circular data structure with special properties"""
    
    def __init__(self, elements):
        self.elements = list(elements)
        self.current_index = 0
    
    def next(self):
        """Get next element in circular fashion"""
        if not self.elements:
            return None
        
        value = self.elements[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.elements)
        return value
    
    def previous(self):
        """Get previous element in circular fashion"""
        if not self.elements:
            return None
        
        self.current_index = (self.current_index - 1) % len(self.elements)
        return self.elements[self.current_index]
    
    def current(self):
        """Get current element"""
        if not self.elements:
            return None
        return self.elements[self.current_index]
    
    def reset(self):
        """Reset to first element"""
        self.current_index = 0
        return self.elements[0] if self.elements else None
    
    def all(self):
        """Get all elements"""
        return self.elements.copy()
    
    def size(self):
        """Get size of mandal"""
        return len(self.elements)
    
    def __str__(self):
        return f"Mandal({self.elements}) at position {self.current_index}"
    
    def __repr__(self):
        return self.__str__()

# =============================================================================
# SEVA (SERVICE) SYSTEM
# =============================================================================

class MantraService:
    """Base class for Mantra services"""
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler
        self.is_running = False
    
    def start(self):
        """Start the service"""
        self.is_running = True
        return f"Service '{self.name}' started"
    
    def stop(self):
        """Stop the service"""
        self.is_running = False
        return f"Service '{self.name}' stopped"
    
    def call(self, *args, **kwargs):
        """Call the service handler"""
        if self.is_running:
            return self.handler(*args, **kwargs)
        return f"Service '{self.name}' is not running"