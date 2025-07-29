#!/usr/bin/env python3.10
"""
Enhanced file expansion using Jinja2 templates with flexible functionality.

Example usage:
    jexpand template.md                           # Print to stdout
    jexpand template.md -o expanded.md            # Write to file
    jexpand template.md --output expanded.md      # Write to file
    jexpand template.md --strict=False            # Non-strict mode

This will process Jinja2 templates with custom functions for file inclusion,
code formatting, and more advanced template features.

Template example:
```template.md
You will be given several files, your goal is to convert the implementation.

<source_implementation>
{{ include_file('/path/to/source/file.py') }}
</source_implementation>

<target_framework>
{{ include_file('/path/to/target/framework/example.py', language='python') }}
</target_framework>

<reference_implementation>
{{ include_file('/path/to/reference/implementation.py') | code_block('python') }}
</reference_implementation>

<!-- Advanced features -->
{% if file_exists('/path/to/optional/file.py') %}
<optional_file>
{{ include_file('/path/to/optional/file.py') }}
</optional_file>
{% endif %}

<!-- Include all files from a folder -->
<all_python_files>
{{ include_folder('/path/to/python/files', pattern='*.py', format_as='blocks') }}
</all_python_files>

<!-- Include all files recursively -->
<all_source_files>
{{ include_folder('/path/to/source', pattern='*', recursive=true, format_as='blocks') }}
</all_source_files>

<!-- Loop through multiple files -->
{% for file_path in ['/path/file1.py', '/path/file2.py'] %}
<{{ loop.index }}>
{{ include_file(file_path) }}
</{{ loop.index }}>
{% endfor %}
```
"""

import os
import sys
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, BaseLoader
from jinja2.exceptions import TemplateNotFound


class StringLoader(BaseLoader):
    """Custom loader for loading templates from strings"""
    def __init__(self, template_string):
        self.template_string = template_string
    
    def get_source(self, environment, template):
        return self.template_string, None, lambda: True


class JinjaFileExpander:
    def __init__(self, template_dir=None, strict_mode=True):
        """
        Initialize the Jinja2 file expander
        
        Args:
            template_dir: Directory to look for template files (optional)
            strict_mode: If True, raises errors for missing files. If False, returns placeholder text.
        """
        self.strict_mode = strict_mode

        if template_dir:
            loader = FileSystemLoader(template_dir)
        else:
            loader = FileSystemLoader(os.getcwd())

        self.env = Environment(
            loader=loader,
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )

        # Register custom functions
        self.env.globals.update(
            {
                "include_file": self._include_file,
                "include_folder": self._include_folder,
                "include_repo_folder": self._include_repo_folder,
                "file_exists": self._file_exists,
                "file_size": self._file_size,
                "file_extension": self._file_extension,
                "basename": self._basename,
                "dirname": self._dirname,
            }
        )

        # Register custom filters
        self.env.filters.update(
            {
                "code_block": self._code_block_filter,
                "indent": self._indent_filter,
                "comment_out": self._comment_out_filter,
                "line_numbers": self._line_numbers_filter,
            }
        )

    def _include_file(self, file_path, encoding='utf-8', default=''):
        """Include the contents of a file"""
        if file_path.startswith('~'):
            file_path = os.path.expanduser(file_path)
        try:
            if not os.path.isfile(file_path):
                if self.strict_mode:
                    raise FileNotFoundError(f"File {file_path} does not exist")
                return default or f"<!-- File not found: {file_path} -->"

            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except Exception as e:
            if self.strict_mode:
                raise
            return default or f"<!-- Error reading file {file_path}: {str(e)} -->"

    def _include_folder(
        self,
        folder_path,
        pattern="*",
        recursive=False,
        format_as="xml",
        separator="\n\n",
        encoding="utf-8",
        include_folder_name=True,
    ):
        """
        Include contents of all files in a folder

        Args:
            folder_path: Path to the folder
            pattern: File pattern to match (e.g., '*.py', '*.txt', '*')
            recursive: If True, search subdirectories recursively
            format_as: How to format the output:
                - 'content': Just concatenated file contents
                - 'blocks': Each file wrapped in a labeled block
                - 'dict': Return as dictionary with filename: content pairs
            separator: String to separate file contents (only for 'content' format)
            encoding: File encoding to use
        """
        import glob

        if folder_path.startswith("~"):
            folder_path = os.path.expanduser(folder_path)

        try:
            if not os.path.isdir(folder_path):
                if self.strict_mode:
                    raise FileNotFoundError(f"Folder {folder_path} does not exist")
                return f"<!-- Folder not found: {folder_path} -->"

            # Build glob pattern
            if recursive:
                glob_pattern = os.path.join(folder_path, "**", pattern)
                file_paths = glob.glob(glob_pattern, recursive=True)
            else:
                glob_pattern = os.path.join(folder_path, pattern)
                file_paths = glob.glob(glob_pattern)

            # Filter to only include files (not directories)
            file_paths = [f for f in file_paths if os.path.isfile(f)]
            file_paths.sort()  # Sort for consistent ordering

            if not file_paths:
                message = f"<!-- No files found matching pattern '{pattern}' in {folder_path} -->"
                if self.strict_mode:
                    raise FileNotFoundError(f"No files found matching pattern '{pattern}' in {folder_path}")
                return message

            # Process files based on format
            if format_as == "dict":
                result = {}
                for file_path in file_paths:
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            relative_path = os.path.relpath(file_path, folder_path)
                            result[relative_path] = f.read()
                    except Exception as e:
                        if self.strict_mode:
                            raise
                        result[relative_path] = f"<!-- Error reading file: {str(e)} -->"
                return result
            elif format_as == "xml":
                xml_content = []
                for file_path in file_paths:
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            content = f.read()
                            relative_path = os.path.relpath(file_path, folder_path)
                            if include_folder_name:
                                base_name = os.path.basename(folder_path)
                                relative_path = f"{base_name}/{relative_path}"
                            xml_content.append(f"<file path='{relative_path}'>")
                            xml_content.append(content)
                            xml_content.append("</file>")
                    except Exception as e:
                        if self.strict_mode:
                            raise
                        xml_content.append(f"<file path='{relative_path}'>")
                        xml_content.append(f"<!-- Error reading file: {str(e)} -->")
                        xml_content.append("</file>")
                return "\n\n".join(xml_content)

            elif format_as == "blocks":
                blocks = []
                for file_path in file_paths:
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            content = f.read()
                            relative_path = os.path.relpath(file_path, folder_path)
                            block = f"<!-- File: {relative_path} -->\n{content}"
                            blocks.append(block)
                    except Exception as e:
                        if self.strict_mode:
                            raise
                        error_msg = f"<!-- File: {relative_path} - Error: {str(e)} -->"
                        blocks.append(error_msg)
                return "\n\n".join(blocks)

            else:  # format_as == 'content'
                contents = []
                for file_path in file_paths:
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            contents.append(f.read())
                    except Exception as e:
                        if self.strict_mode:
                            raise
                        error_msg = f"<!-- Error reading {file_path}: {str(e)} -->"
                        contents.append(error_msg)
                return separator.join(contents)

        except Exception as e:
            if self.strict_mode:
                raise
            return f"<!-- Error processing folder {folder_path}: {str(e)} -->"

    def _file_exists(self, file_path):
        """Check if a file exists"""
        return os.path.isfile(file_path)

    def _file_size(self, file_path):
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except:
            return 0

    def _file_extension(self, file_path):
        """Get file extension"""
        return Path(file_path).suffix

    def _basename(self, file_path):
        """Get basename of file"""
        return os.path.basename(file_path)

    def _dirname(self, file_path):
        """Get directory name of file"""
        return os.path.dirname(file_path)

    def _code_block_filter(self, content, language=''):
        """Wrap content in markdown code block"""
        return f"```{language}\n{content}\n```"

    def _indent_filter(self, content, spaces=4):
        """Indent each line with specified number of spaces"""
        indent = ' ' * spaces
        return '\n'.join(indent + line for line in content.splitlines())

    def _comment_out_filter(self, content, comment_char='#'):
        """Comment out each line"""
        return '\n'.join(f"{comment_char} {line}" for line in content.splitlines())

    def _line_numbers_filter(self, content, format="short"):
        """
        Add line numbers to content

        Args:
            content: The text content to add line numbers to
            format: How to format line numbers:
                - "full": "line 1 | content"
                - "short": "1 | content"
        """
        lines = content.splitlines()
        if format == "full":
            numbered_lines = [f"line {i+1} | {line}" for i, line in enumerate(lines)]
        else:  # short format
            numbered_lines = [f"{i+1} | {line}" for i, line in enumerate(lines)]
        return "\n".join(numbered_lines)

    def expand_string(self, template_string, context=None):
        """Expand a template string"""
        context = context or {}
        template = self.env.from_string(template_string)
        return template.render(**context)

    def expand_file(self, template_path, context=None, output_path=None):
        """Expand a template file"""
        context = context or {}

        # Read the template content directly
        if os.path.isabs(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        else:
            # Try relative path first, then direct path
            try:
                # Check if file exists in template directory
                template_file_path = os.path.join(
                    (
                        self.env.loader.searchpath[0]
                        if hasattr(self.env.loader, "searchpath")
                        else os.getcwd()
                    ),
                    os.path.basename(template_path),
                )
                if os.path.isfile(template_file_path):
                    with open(template_file_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
                else:
                    # Try direct path
                    with open(template_path, "r", encoding="utf-8") as f:
                        template_content = f.read()
            except:
                # Fallback to direct path
                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()

        # Auto-detect and convert old {file_path} syntax to Jinja2
        import re

        # Convert standalone {file_path} to {{ include_file('file_path') }}
        # Only convert simple {something} that's not already Jinja2 syntax
        # Skip {% %}, {{ }}, {# #} patterns
        lines = template_content.split('\n')
        converted_lines = []
        
        for line in lines:
            # Don't convert lines that already contain Jinja2 syntax
            if '{%' in line or '{{' in line or '{#' in line:
                converted_lines.append(line)
            else:
                # Convert simple {file_path} patterns
                converted_line = re.sub(r'\{([^{}]+)\}', r"{{ include_file('\1') }}", line)
                converted_lines.append(converted_line)
        
        template_content = '\n'.join(converted_lines)

        # Create template from the (possibly converted) content
        template = self.env.from_string(template_content)
        result = template.render(**context)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
        else:
            print(result, end="")  # Don't add extra newline

        return result

    def compile_to_intermediate(self, template_path, context=None, intermediate_path=None):
        """
        Compile template to intermediate form (Feature 1.5)
        
        This converts the template syntax but doesn't fully expand includes yet.
        Useful for debugging or two-stage processing.
        """
        context = context or {}
        
        # Read the template content
        if os.path.isabs(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        else:
            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()
        
        # Auto-detect and convert old {file_path} syntax to Jinja2
        import re
        
        # Convert standalone {file_path} to {{ include_file('file_path') }}
        # Only convert simple {something} that's not already Jinja2 syntax
        # Skip {% %}, {{ }}, {# #} patterns
        lines = template_content.split('\n')
        converted_lines = []
        
        for line in lines:
            # Don't convert lines that already contain Jinja2 syntax
            if '{%' in line or '{{' in line or '{#' in line:
                converted_lines.append(line)
            else:
                # Convert simple {file_path} patterns
                converted_line = re.sub(r'\{([^{}]+)\}', r"{{ include_file('\1') }}", line)
                converted_lines.append(converted_line)
        
        template_content = '\n'.join(converted_lines)
        
        # This is the intermediate form - converted but not expanded
        intermediate_content = template_content
        
        if intermediate_path:
            with open(intermediate_path, 'w', encoding='utf-8') as f:
                f.write(intermediate_content)
        
        return intermediate_content

    def expand_intermediate(self, intermediate_content, context=None, output_path=None):
        """
        Expand intermediate form to final form (Feature 1.5)
        
        Takes the intermediate template and fully expands it.
        """
        context = context or {}
        
        # Create template from intermediate content and render
        template = self.env.from_string(intermediate_content)
        result = template.render(**context)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result)
        else:
            print(result, end="")
        
        return result

    def simple_expand(self, template_path, context=None, output_path=None):
        """
        Simple expansion with {file_path} syntax conversion to Jinja2

        Converts {/path/to/file} to {{ include_file('/path/to/file') }}
        for backward compatibility and simpler template syntax.
        """
        context = context or {}

        # Read the template file
        with open(template_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Convert {/path/to/file} to {{ include_file('/path/to/file') }}
        import re

        converted = re.sub(r"\{([^}]+)\}", r"{{ include_file('\1') }}", content)

        # Expand using the converted template
        result = self.expand_string(converted, context)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result)
        else:
            print(result, end="")

        return result

    def _include_repo_folder(self, url, dirs_to_checkout, branch="main", format_as="xml"):
        """Include files from a remote Git repository"""
        try:
            from .load_from_repo import download_repo_folder, filter_files
            
            content_dict = download_repo_folder(url, dirs_to_checkout, branch)
            
            if format_as == "xml":
                xml_content = []
                for path, content in content_dict.items():
                    # Remove leading slash from path
                    clean_path = path.lstrip('/')
                    xml_content.append(f"<file path='{clean_path}'>")
                    xml_content.append(content)
                    xml_content.append("</file>")
                return "\n\n".join(xml_content)
            elif format_as == "blocks":
                blocks = []
                for path, content in content_dict.items():
                    clean_path = path.lstrip('/')
                    block = f"<!-- File: {clean_path} -->\n{content}"
                    blocks.append(block)
                return "\n\n".join(blocks)
            elif format_as == "dict":
                return {path.lstrip('/'): content for path, content in content_dict.items()}
            else:  # format_as == "content"
                return "\n\n".join(content_dict.values())
                
        except Exception as e:
            if self.strict_mode:
                raise RuntimeError(f"Error downloading from {url}: {str(e)}")
            return f"<!-- Error downloading from {url}: {str(e)} -->"


# def expand_file(file_path, output_path=None, strict=True, template_dir=None):
#         expander = JinjaFileExpander(
#             template_dir=template_dir, strict_mode=strict
#         )

#         # Expand template
#         expander.expand_file(
#             template_path=file_path, context={}, output_path=output_path
#         )


def main():
    """Main entry point with argparse"""
    parser = argparse.ArgumentParser(
        description="Enhanced file expansion using Jinja2 templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  jexpand template.md                    # Print to stdout
  jexpand template.md -o expanded.md     # Write to file
  jexpand template.md --output result.md # Write to file
  jexpand template.md --no-strict        # Non-strict mode (don't fail on missing files)
  jexpand template.md --intermediate intermediate.md # Compile to intermediate form
  jexpand template.md --intermediate intermediate.md --final final.md # Two-stage compilation

Template Features:
  {{ include_file('path/to/file') }}           # Include file contents
  {{ include_file('file.py') | code_block('python') }}  # Include with syntax highlighting
  {{ include_folder('path/to/folder') }}       # Include all files in folder
  {{ include_folder('src', pattern='*.py') }}  # Include Python files only
  {{ include_folder('src', recursive=true, format_as='blocks') }}  # Recursive with file labels
  {{ include_repo_folder('https://github.com/user/repo', ['src', 'docs']) }}  # Include from Git repo
  {% if file_exists('optional.txt') %}        # Conditional inclusion
  {{ file_size('data.csv') }}                 # File size in bytes
  {{ basename('/path/to/file.txt') }}         # Get filename
        """,
    )

    parser.add_argument("input_file", help="Path to the template file to expand")

    parser.add_argument(
        "-o",
        "--output",
        dest="output_file",
        help="Output file path (default: print to stdout)",
    )

    parser.add_argument(
        "--intermediate",
        dest="intermediate_file",
        help="Compile to intermediate form and save to this file",
    )

    parser.add_argument(
        "--final",
        dest="final_file",
        help="When using --intermediate, expand the intermediate form to this final file",
    )

    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Strict mode: fail on missing files (default: True)",
    )

    parser.add_argument(
        "--no-strict",
        action="store_false",
        dest="strict",
        help="Non-strict mode: show placeholders for missing files",
    )

    parser.add_argument(
        "--template-dir",
        help="Directory to search for template files (default: current directory)",
    )

    parser.add_argument("--version", action="version", version="jexpand 1.0.4")

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.isfile(args.input_file):
        print(f"Error: Template file '{args.input_file}' not found", file=sys.stderr)
        sys.exit(1)

    # Create expander
    try:
        # expand_file(args.input_file, args.output_file, args.strict, args.template_dir)
        
        expander = JinjaFileExpander(template_dir=args.template_dir, strict_mode=args.strict)
        
        if args.intermediate_file:
            # Two-stage compilation (Feature 1.5)
            intermediate_content = expander.compile_to_intermediate(
                args.input_file, intermediate_path=args.intermediate_file
            )
            
            if args.final_file:
                # Expand intermediate to final
                expander.expand_intermediate(intermediate_content, output_path=args.final_file)
                print(f"Template compiled to intermediate: {args.intermediate_file}", file=sys.stderr)
                print(f"Intermediate expanded to final: {args.final_file}", file=sys.stderr)
            else:
                print(f"Template compiled to intermediate: {args.intermediate_file}", file=sys.stderr)
        else:
            # Standard single-stage expansion
            expand_file(args.input_file, args.output_file, args.strict, args.template_dir)
            
            if args.output_file:
                print(f"Template expanded successfully to: {args.output_file}", file=sys.stderr)

    except Exception as e:
        import traceback
        print(f"Error: {str(e)}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


# Backward compatibility function for fire-based usage
def expand_file(file_path, output_path=None, strict=True, template_dir=None, **context):
    """
    Backward compatibility function for fire-based usage

    Args:
        file_path: Path to template file
        output_path: Optional output file path
        strict: Whether to use strict mode (default: True)
        template_dir: Directory to search for template files (optional)
        **context: Additional context variables for template
    """
    expander = JinjaFileExpander(template_dir=template_dir, strict_mode=strict)
    return expander.expand_file(file_path, context, output_path)


# Example usage and backward compatibility
def simple_expand(file_path):
    """Simple expansion for backward compatibility with original script"""
    expander = JinjaFileExpander(strict_mode=True)
    
    # Read the file and convert simple {file_path} syntax to Jinja2
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Convert {/path/to/file} to {{ include_file('/path/to/file') }}
    import re
    converted = re.sub(r'\{([^}]+)\}', r"{{ include_file('\1') }}", content)
    
    result = expander.expand_string(converted)
    print(result)


if __name__ == "__main__":
    main()
