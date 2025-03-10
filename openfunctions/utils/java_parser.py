import json
import javalang
import re

def parse_java_function_call(source_code):
    """
    Parses the given Java function call code and extracts information about method invocations.

    Args:
        source_code (str): The Java source code to parse.

    Returns:
        dict: A dictionary containing information about the method invocation, including the function name and its parameters.
              If there is an error during parsing, None is returned.
    """
    try:
        # Add wrapper to make it valid Java for parsing
        wrapped_code = f"class Wrapper {{ void method() {{ {source_code} }} }}"
        
        # Parse the Java code
        tree = javalang.parse.parse(wrapped_code)
        
        # Extract method invocation
        method_invocations = list(tree.filter(javalang.tree.MethodInvocation))
        
        if not method_invocations:
            return None
        
        # Get the first method invocation (usually the main one in simple calls)
        method_invocation = method_invocations[0]
        
        # Extract function name
        if method_invocation.qualifier:
            function_name = f"{method_invocation.qualifier}.{method_invocation.member}"
        else:
            function_name = method_invocation.member
        
        # Extract parameters
        parameters = {}
        
        # Process regular arguments (unnamed)
        unnamed_args = []
        for arg in method_invocation.arguments:
            # For unnamed parameters, we add to a list under the None key
            if isinstance(arg, javalang.tree.Literal) or isinstance(arg, javalang.tree.Name):
                if isinstance(arg, javalang.tree.Literal):
                    value = arg.value
                else:
                    value = arg.value
                unnamed_args.append(value)
        
        if unnamed_args:
            parameters[None] = unnamed_args
        
        # Since javalang doesn't directly support named parameters (Java doesn't have them natively),
        # we'll need to use regex to extract named parameters from the original source
        named_params_pattern = r'(\w+)\s*=\s*([^,\)]+)'
        named_params = re.findall(named_params_pattern, source_code)
        
        for name, value in named_params:
            # Clean up the value by removing extra whitespace
            value = value.strip()
            parameters[name] = value
        
        # Extract complex object creation expressions
        object_creation_pattern = r'(\w+)\s*=\s*new\s+([\w<>\[\]]+)(\(.*?\))'
        object_creations = re.findall(object_creation_pattern, source_code)
        
        for name, obj_type, args in object_creations:
            parameters[name] = f"new {obj_type}{args}"
        
        # Handle array creation
        array_creation_pattern = r'(\w+)\s*=\s*(new\s+[\w<>]+\[\]\{.*?\})'
        array_creations = re.findall(array_creation_pattern, source_code)
        
        for name, array_expr in array_creations:
            parameters[name] = array_expr
        
        return {
            "function": {
                "name": function_name,
                "parameters": parameters
            }
        }
    
    except Exception as e:
        print(f"Error parsing Java code: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Valid Java source code
    source_code = """FileSystemsTest.execute(a, b, node=testRootNode, env=testEnv, contextArguments=new Object[]{'local', '/home/user', false, true, true}, frameArguments=new Object[]{}, arraylist=new ArrayList<>(Arrays.asList("include_defaults", true, "TOXCONTENT_SKIP_RUNTIME", true)))"""
    
    result = parse_java_function_call(source_code)
    print(json.dumps(result, indent=2))
