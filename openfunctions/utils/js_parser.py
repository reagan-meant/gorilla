import json
import esprima
import re

def parse_javascript_function_call(source_code):
    """
    Parses the given JavaScript function call code and extracts information about function calls.

    Args:
        source_code (str): The JavaScript source code to parse.

    Returns:
        dict: A dictionary containing information about the function call, including the function name and its parameters.
              If there is an error during parsing, None is returned.
    """
    try:
        # Parse the JavaScript code
        parsed = esprima.parseScript(source_code)
        
        # Get the first expression statement (typically contains the function call)
        if (len(parsed.body) > 0 and 
            hasattr(parsed.body[0], 'type') and 
            parsed.body[0].type == 'ExpressionStatement'):
            
            expression = parsed.body[0].expression
            
            # Check if it's a function call
            if hasattr(expression, 'type') and expression.type == 'CallExpression':
                # Extract the function name
                if hasattr(expression.callee, 'name'):
                    function_name = expression.callee.name
                elif hasattr(expression.callee, 'property') and hasattr(expression.callee.property, 'name'):
                    # Handle object method calls like object.method()
                    obj_name = ''
                    if hasattr(expression.callee.object, 'name'):
                        obj_name = expression.callee.object.name
                    elif hasattr(expression.callee.object, 'type') and expression.callee.object.type == 'CallExpression':
                        # Handle chained calls like document.getElementById().method()
                        if hasattr(expression.callee.object.callee, 'property'):
                            obj_name = f"{expression.callee.object.callee.object.name}.{expression.callee.object.callee.property.name}()"
                    function_name = f"{obj_name}.{expression.callee.property.name}" if obj_name else expression.callee.property.name
                else:
                    # Handle other cases or return a placeholder
                    function_name = "unknown_function"
                
                # Since esprima doesn't directly support named parameters in the same way as your original code,
                # we'll use regex to extract named parameters from the original source
                # This is similar to the approach used in the Java parser
                
                parameters = {}
                
                # Extract named parameters using regex
                named_params_pattern = r'(\w+)\s*=\s*([^,\)]+)'
                named_params = re.findall(named_params_pattern, source_code)
                
                for name, value in named_params:
                    value = value.strip()
                    parameters[name] = value
                
                # Handle unnamed parameters
                if not parameters and hasattr(expression, 'arguments') and expression.arguments:
                    unnamed_args = []
                    for arg in expression.arguments:
                        if hasattr(arg, 'value') and arg.value is not None:
                            unnamed_args.append(str(arg.value))
                        elif hasattr(arg, 'name'):
                            unnamed_args.append(arg.name)
                    
                    if unnamed_args:
                        parameters[None] = unnamed_args
                
                return {
                    "function": {
                        "name": function_name,
                        "parameters": parameters
                    }
                }
        
        return None
    
    except Exception as e:
        print(f"Error parsing JavaScript code: {e}")
        return None

# Example usage
if __name__ == "__main__":
    source_code = """markdownRenderComplete(elem=document.getElementById('contentArea'), rendered=true, array=[1,2,3], array2=new Array(1,2,3), dictionary={'key':'value'})"""
    
    result = parse_javascript_function_call(source_code)
    print(source_code)
    print(json.dumps(result, indent=2))