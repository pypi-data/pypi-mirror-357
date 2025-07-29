from typing import Dict, List, Any, Optional, Union
import threading
import time
from .ast_nodes import *

class Environment:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.functions = {}
    
    def define(self, name, value):
        self.variables[name] = value
    
    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        return None
    
    def set(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent and name in self.parent.variables:
            self.parent.set(name, value)
        else:
            self.variables[name] = value
    
    def define_function(self, name, func):
        self.functions[name] = func
    
    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        if self.parent:
            return self.parent.get_function(name)
        return None

class MantraFunction:
    def __init__(self, name, params, body, closure):
        self.name = name
        self.params = params
        self.body = body
        self.closure = closure

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class SimpleInterpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env
        self.yantra_apps = {}  # Store GUI applications
        self.services = {}     # Store running services
        self.setup_builtins()
    
    def setup_builtins(self):
        """Enhanced built-ins with advanced features"""
        
        # Basic Sanskrit functions
        def prakash(*args):
            print(*args)
            return None
        
        def lambh(obj):
            if obj is None:
                return 0
            elif hasattr(obj, 'lambh'):
                return obj.lambh()
            try:
                return len(str(obj))
            except:
                return 0
        
        def shabd(obj):
            return str(obj) if obj is not None else "shunya"
        
        def ank(obj):
            try:
                return int(float(obj)) if obj is not None else 0
            except:
                return 0
        
        # 🔥 ADVANCED BUILT-IN FUNCTIONS
        
        def yantra_create(element_type, **properties):
            """Create a GUI element"""
            widget = YantraWidget(element_type, properties)
            return widget
        
        def yantra_show(app_name="default"):
            """Show the GUI application"""
            if app_name not in self.yantra_apps:
                self.yantra_apps[app_name] = YantraApplication()
            
            app = self.yantra_apps[app_name]
            return app.run()
        
        def yantra_add(widget, app_name="default"):
            """Add widget to application"""
            if app_name not in self.yantra_apps:
                self.yantra_apps[app_name] = YantraApplication()
            
            app = self.yantra_apps[app_name]
            
            # Handle window creation separately
            if widget.widget_type == "window":
                app.main_window = widget.create_widget(None)
            else:
                app.add_widget(widget)
            
            return widget
        
        def shakti_execute(expression_type, **properties):
            """Execute a power expression"""
            if expression_type == "web_server":
                return ShaktiProcessor.process_web_server(properties)
            elif expression_type == "database":
                return ShaktiProcessor.process_database(properties)
            elif expression_type == "file":
                return ShaktiProcessor.process_file_operations(properties)
            else:
                return f"Unknown Shakti expression: {expression_type}"
        
        def sutra_compose(*functions):
            """Compose functions"""
            return SutraComposer.compose(*functions)
        
        def raga_flow(data, *transformations):
            """Process data flow"""
            return RagaProcessor.process_flow(data, transformations)
        
        def mandal_create(*elements):
            """Create circular data structure"""
            return MandalStructure(elements)
        
        def seva_start(name, handler):
            """Start a service"""
            service = MantraService(name, handler)
            self.services[name] = service
            return service.start()
        
        def seva_stop(name):
            """Stop a service"""
            if name in self.services:
                return self.services[name].stop()
            return f"Service '{name}' not found"
        
        def seva_call(name, *args, **kwargs):
            """Call a service"""
            if name in self.services:
                return self.services[name].call(*args, **kwargs)
            return f"Service '{name}' not found"
        
        # Array methods
        def array_create(*elements):
            """Create an enhanced array"""
            return MantraArray(elements)
        
        # Time functions
        def samay():
            """Get current time (samay = time)"""
            return time.time()
        
        def vishram(seconds):
            """Sleep (vishram = rest)"""
            time.sleep(seconds)
            return None
        
        # Register all functions
        builtins = {
            # Basic functions
            'prakash': prakash,
            'lambh': lambh,
            'shabd': shabd,
            'ank': ank,
            # English aliases
            'print': prakash,
            'len': lambh,
            'str': shabd,
            'int': ank,
            # Advanced functions
            'yantra_create': yantra_create,
            'yantra_show': yantra_show,
            'yantra_add': yantra_add,
            'shakti_execute': shakti_execute,
            'sutra_compose': sutra_compose,
            'raga_flow': raga_flow,
            'mandal_create': mandal_create,
            'seva_start': seva_start,
            'seva_stop': seva_stop,
            'seva_call': seva_call,
            'array_create': array_create,
            'samay': samay,
            'vishram': vishram,
        }
        
        for name, func in builtins.items():
            self.global_env.define_function(name, func)
    
    def interpret(self, node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, None)
        if method:
            return method(node)
        else:
            print(f"Warning: No visitor for {type(node).__name__}")
            return None
    
    # Basic visitor methods (unchanged)
    
    def visit_ProgramNode(self, node):
        result = None
        for statement in node.statements:
            try:
                result = self.interpret(statement)
            except ReturnValue as ret:
                return ret.value
        return result
    
    def visit_NumberNode(self, node):
        return node.value
    
    def visit_StringNode(self, node):
        return node.value
    
    def visit_BooleanNode(self, node):
        return node.value
    
    def visit_NullNode(self, node):
        return None
    
    def visit_IdentifierNode(self, node):
        return self.current_env.get(node.name)
    
    def visit_BinaryOpNode(self, node):
        left = self.interpret(node.left)
        right = self.interpret(node.right)
        
        # Handle None values
        if left is None:
            left = 0
        if right is None:
            right = 0
        
        try:
            if node.operator == '+':
                return left + right
            elif node.operator == '-':
                return left - right
            elif node.operator == '*':
                return left * right
            elif node.operator == '/':
                return left / right if right != 0 else 0
            elif node.operator == '==':
                return left == right
            elif node.operator == '!=':
                return left != right
            elif node.operator == '<':
                return left < right
            elif node.operator == '>':
                return left > right
            elif node.operator == '<=':
                return left <= right
            elif node.operator == '>=':
                return left >= right
        except:
            return 0
    
    def visit_AssignmentNode(self, node):
        value = self.interpret(node.value)
        self.current_env.set(node.name, value)
        return value
    
    def visit_VariableDeclarationNode(self, node):
        value = None
        if node.value:
            value = self.interpret(node.value)
        self.current_env.define(node.name, value)
        return value
    
    def visit_FunctionDefNode(self, node):
        func = MantraFunction(node.name, node.params, node.body, self.current_env)
        self.current_env.define_function(node.name, func)
        return func
    
    def visit_FunctionCallNode(self, node):
        func = self.current_env.get_function(node.name)
        if not func:
            # Try as a method on an object
            return None
        
        args = [self.interpret(arg) for arg in node.args]
        
        # Built-in function
        if callable(func):
            try:
                return func(*args)
            except Exception as e:
                print(f"Error calling {node.name}: {e}")
                return None
        
        # User-defined function
        if isinstance(func, MantraFunction):
            if len(args) != len(func.params):
                print(f"Function {func.name} expects {len(func.params)} arguments, got {len(args)}")
                return None
            
            # Create new environment
            func_env = Environment(func.closure)
            for param, arg in zip(func.params, args):
                func_env.define(param, arg)
            
            # Execute function
            prev_env = self.current_env
            self.current_env = func_env
            
            try:
                result = None
                for statement in func.body:
                    result = self.interpret(statement)
                return result
            except ReturnValue as ret:
                return ret.value
            finally:
                self.current_env = prev_env
        
        return None
    
    def visit_IfNode(self, node):
        condition = self.interpret(node.condition)
        
        if condition:
            result = None
            for stmt in node.then_branch:
                result = self.interpret(stmt)
            return result
        elif node.else_branch:
            result = None
            for stmt in node.else_branch:
                result = self.interpret(stmt)
            return result
        return None
    
    def visit_LoopNode(self, node):
        result = None
        count = 0
        max_iterations = 10000  # Prevent infinite loops
        
        while count < max_iterations:
            condition = self.interpret(node.condition)
            if not condition:
                break
            
            for stmt in node.body:
                result = self.interpret(stmt)
            count += 1
        
        return result
    
    def visit_ReturnNode(self, node):
        value = None
        if node.value:
            value = self.interpret(node.value)
        raise ReturnValue(value)
    
    # 🔥 NEW: Advanced visitor methods
    
    def visit_ArrayNode(self, node):
        """Visit array literal"""
        elements = [self.interpret(elem) for elem in node.elements]
        return elements  # Return as Python list for now
    
    def visit_PropertyAccessNode(self, node):
        """Visit property access"""
        obj = self.interpret(node.object)
        if obj is None:
            return None
        
        # Handle built-in properties
        if hasattr(obj, node.property):
            attr = getattr(obj, node.property)
            if callable(attr):
                return attr
            return attr
        
        # Handle dictionary-like access
        if isinstance(obj, dict) and node.property in obj:
            return obj[node.property]
        
        return None
    
    def visit_MethodCallNode(self, node):
        """Visit method call"""
        obj = self.interpret(node.object)
        if obj is None:
            return None
        
        args = [self.interpret(arg) for arg in node.args]
        
        # Handle built-in methods
        if hasattr(obj, node.method):
            method = getattr(obj, node.method)
            if callable(method):
                try:
                    return method(*args)
                except Exception as e:
                    print(f"Error calling method {node.method}: {e}")
                    return None
        
        return None
    
    def visit_YantraDeclarationNode(self, node):
        """Visit Yantra (GUI) declaration"""
        # Evaluate properties
        props = {}
        for key, value_node in node.properties.items():
            props[key] = self.interpret(value_node)
        
        # Create widget
        widget = YantraWidget(node.element_type, props)
        
        # Store in environment
        self.current_env.define(node.name, widget)
        
        # Auto-add to default app if it's a widget
        if node.element_type != "window":
            if "default" not in self.yantra_apps:
                self.yantra_apps["default"] = YantraApplication()
            self.yantra_apps["default"].add_widget(widget)
        else:
            # For windows, create the app
            if "default" not in self.yantra_apps:
                self.yantra_apps["default"] = YantraApplication()
            self.yantra_apps["default"].main_window = widget.create_widget(None)
        
        return widget
    
    def visit_ShaktiDeclarationNode(self, node):
        """Visit Shakti (power expression) declaration"""
        # Evaluate properties
        props = {}
        for key, value_node in node.properties.items():
            props[key] = self.interpret(value_node)
        
        # Execute the power expression
        result = None
        if node.expression_type == "web_server":
            result = ShaktiProcessor.process_web_server(props)
        elif node.expression_type == "database":
            result = ShaktiProcessor.process_database(props)
        elif node.expression_type == "file":
            result = ShaktiProcessor.process_file_operations(props)
        else:
            result = f"Unknown Shakti expression: {node.expression_type}"
        
        # Store result
        self.current_env.define(node.name, result)
        return result
    
    def visit_SutraDeclarationNode(self, node):
        """Visit Sutra (function composition) declaration"""
        # Evaluate functions
        functions = []
        for func_node in node.functions:
            func = self.interpret(func_node)
            if func:
                functions.append(func)
        
        # Create composed function
        composed = SutraComposer.compose(*functions)
        
        # Store in environment
        self.current_env.define_function(node.name, composed)
        return composed
    
    def visit_RagaDeclarationNode(self, node):
        """Visit Raga (data flow) declaration"""
        # Evaluate source
        source = self.interpret(node.source)
        
        # Apply transformations
        result = source
        for transform_node in node.transformations:
            if isinstance(transform_node, FunctionCallNode):
                # Get the function
                func = self.current_env.get_function(transform_node.name)
                if func:
                    args = [self.interpret(arg) for arg in transform_node.args]
                    if callable(func):
                        result = func(result, *args)
        
        # Store result
        self.current_env.define(node.name, result)
        return result
    
    def visit_MandalDeclarationNode(self, node):
        """Visit Mandal (circular data) declaration"""
        # Evaluate elements
        elements = [self.interpret(elem) for elem in node.elements]
        
        # Create mandal structure
        mandal = MandalStructure(elements)
        
        # Store in environment
        self.current_env.define(node.name, mandal)
        return mandal
    
    def visit_SevaDefinitionNode(self, node):
        """Visit Seva (service) definition"""
        # Create service function
        def service_handler(*args):
            # Create new environment for service
            service_env = Environment(self.current_env)
            
            # Bind parameters
            for i, (param, arg) in enumerate(zip(node.params, args)):
                service_env.define(param, arg)
            
            # Execute service body
            prev_env = self.current_env
            self.current_env = service_env
            
            try:
                result = None
                for statement in node.body:
                    result = self.interpret(statement)
                return result
            except ReturnValue as ret:
                return ret.value
            finally:
                self.current_env = prev_env
        
        # Create and start service
        service = MantraService(node.name, service_handler)
        self.services[node.name] = service
        service.start()
        
        # Store in environment
        self.current_env.define_function(node.name, service_handler)
        return service