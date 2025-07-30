"""
Dr. Doc - A documentation processing tool for identifying and correcting errors 
in markdown, reStructuredText, and plain text files using AI language models.
"""

__version__ = "0.1.0"
__author__ = "Murat Keceli"
__email__ = "keceli@anl.gov"

from .drdoc import main, process_documentation_file, estimate_tokens, prepend_filename_with_fixed

__all__ = ["main", "process_documentation_file", "estimate_tokens", "prepend_filename_with_fixed"]
