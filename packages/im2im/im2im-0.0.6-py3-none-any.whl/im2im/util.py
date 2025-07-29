import re
import inspect


def instance_code_template(code_template, input, output):
    """
        Replaces 'var' with 'input' and 'return' with 'output' in the provided code string.
        Ensures replacements are not part of other strings or words.

        Examples:
            >>> code_str = "return var[:, :, ::-1]"
            >>> new_code_str = instance_code_template(code_str, 'source_image', 'target_image')
            >>> print(new_code_str)
            target_image = source_image[:, :, ::-1]
        """
    # Replace 'var' with the input variable, ensuring it's not part of another word
    var_pattern = re.compile(r'\bvar\b')  # Word boundary ensures exact match
    code_str = var_pattern.sub(input, code_template)

    # Replace 'return' with the output variable, ensuring it's not part of another word
    return_pattern = re.compile(r'\breturn\b')  # Word boundary ensures exact match
    code_str = return_pattern.sub(f'{output} =', code_str)

    return code_str.strip()


def func_obj_to_str(func_obj):
    return inspect.getsource(func_obj)


def exclude_key_from_list(keys, exclude_key):
    """
    Excludes a specific key from a list of keys.

    Parameters:
    - keys: List of keys from which to exclude.
    - exclude_key: The key to be excluded from the list.

    Returns:
    - A new list with the specified key excluded.
    """
    # New list with the exclude_key removed
    filtered_keys = [key for key in keys if key != exclude_key]
    return filtered_keys
