#!/usr/bin/env python3
"""
Docxtpl Word Template Syntax Error Checker
A comprehensive tool for validating docxtpl templates and generating detailed reports.
"""

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from zipfile import ZipFile
import xml.etree.ElementTree as ET

try:
    from jinja2 import Environment, TemplateSyntaxError
except ImportError:
    print("Error: jinja2 library is required. Please install with: pip install jinja2")
    sys.exit(1)


class TemplateIssue:
    """Represents a template issue found during validation."""

    SEVERITY_ERROR = "ERROR"
    SEVERITY_WARNING = "WARNING"
    SEVERITY_INFO = "INFO"

    def __init__(self, severity: str, category: str, message: str,
                 location: str = "", line_number: int = 0, suggestion: str = "", context: str = ""):
        self.severity = severity
        self.category = category
        self.message = message
        self.location = location
        self.line_number = line_number
        self.suggestion = suggestion
        self.context = context
        self.timestamp = datetime.now()

    def __str__(self):
        """String representation of the issue."""
        return f"{self.severity}: {self.message}"


class LanguageStrings:
    """Language strings for internationalization."""
    
    EN = {
        'validation_starting': 'Starting validation: {}',
        'validation_complete': 'Validation complete. Found {} issues.',
        'generating_report': 'Generating report: {}',
        'report_generated': 'Report generated successfully',
        'validation_results': 'Validation Results:',
        'errors': 'Errors',
        'warnings': 'Warnings',
        'info': 'Info',
        'detailed_report_saved': 'Detailed report saved to: {}',
        'validation_failed': '❌ Validation failed with {} errors',
        'validation_passed': '✅ Template validation passed!',
        'validation_warnings': '⚠️  Validation completed with {} warnings',
        'report_title': 'Docxtpl Template Validation Report',
        'generated': 'Generated',
        'summary': 'Summary',
        'total_issues': 'Total Issues',
        'location': 'Location',
        'line': 'Line',
        'suggestion': '💡 Suggestion',
        'context': '📍 Context',
        'no_issues': '🎉 No issues found in this category!',
        'best_practices': 'Docxtpl Template Best Practices',
        'basic_syntax': 'Basic Syntax',
        'docxtpl_prefixes': 'Docxtpl Specific Prefix Tags',
        'filters': 'Filters',
        'examples': 'Examples',
        # Error categories
        'template_structure': 'Template Structure',
        'docxtpl_structure': 'Docxtpl Structure',
        'file_access': 'File Access',
        'jinja2_syntax': 'Jinja2 Syntax',
        'template_parsing': 'Template Parsing',
        'bracket_matching': 'Bracket Matching',
        'quote_matching': 'Quote Matching',
        'expression_syntax': 'Expression Syntax',
        'docxtpl_image': 'Docxtpl Image',
        'docxtpl_subdoc': 'Docxtpl Subdoc',
        'docxtpl_paragraph_control': 'Docxtpl Paragraph Control',
        'docxtpl_table_row_control': 'Docxtpl Table Row Control',
        'docxtpl_table_cell_control': 'Docxtpl Table Cell Control',
        'docxtpl_run_control': 'Docxtpl Run Control',
        'code_quality': 'Code Quality',
        'tag_matching': 'Tag Matching',
        # Common locations
        'document': 'Document',
        'overall_template': 'Overall Template',
        'template': 'Template',
        # Common messages and suggestions
        'tag_mismatch_found_instead': '{} tag mismatch: found {} instead of {}',
        'change_to_match_pattern': 'Change {} to {} to match the docxtpl prefix pattern',
        'using_prefix_for_control': 'Using {} prefix for {} control',
        'prefix_used_for_control': '{}{{}} is used for {} level dynamic generation'
    }
    
    ZH = {
        'validation_starting': '开始验证: {}',
        'validation_complete': '验证完成。发现 {} 个问题。',
        'generating_report': '正在生成报告: {}',
        'report_generated': '报告生成成功',
        'validation_results': '验证结果:',
        'errors': '错误',
        'warnings': '警告',
        'info': '信息',
        'detailed_report_saved': '详细报告已保存到: {}',
        'validation_failed': '❌ 验证失败，发现 {} 个错误',
        'validation_passed': '✅ 模板验证通过！',
        'validation_warnings': '⚠️  验证完成，发现 {} 个警告',
        'report_title': 'Docxtpl 模板验证报告',
        'generated': '生成时间',
        'summary': '摘要',
        'total_issues': '总问题数',
        'location': '位置',
        'line': '行',
        'suggestion': '💡 建议',
        'context': '📍 上下文',
        'no_issues': '🎉 没有发现此类问题！',
        'best_practices': 'Docxtpl 模板最佳实践',
        'basic_syntax': '基本语法',
        'docxtpl_prefixes': 'Docxtpl 特有前缀标签',
        'filters': '过滤器',
        'examples': '示例',
        # Error categories
        'template_structure': '模板结构',
        'docxtpl_structure': 'Docxtpl 结构',
        'file_access': '文件访问',
        'jinja2_syntax': 'Jinja2 语法',
        'template_parsing': '模板解析',
        'bracket_matching': '括号匹配',
        'quote_matching': '引号匹配',
        'expression_syntax': '表达式语法',
        'docxtpl_image': 'Docxtpl 图片',
        'docxtpl_subdoc': 'Docxtpl 子文档',
        'docxtpl_paragraph_control': 'Docxtpl 段落控制',
        'docxtpl_table_row_control': 'Docxtpl 表格行控制',
        'docxtpl_table_cell_control': 'Docxtpl 表格单元格控制',
        'docxtpl_run_control': 'Docxtpl 运行控制',
        'code_quality': '代码质量',
        'tag_matching': '标签匹配',
        # Common locations
        'document': '文档',
        'overall_template': '整体模板',
        'template': '模板',
        # Common messages and suggestions
        'tag_mismatch_found_instead': '{} 标签不匹配：发现 {} 而不是 {}',
        'change_to_match_pattern': '将 {} 更改为 {} 以匹配 docxtpl 前缀模式',
        'using_prefix_for_control': '使用 {} 前缀进行 {} 控制',
        'prefix_used_for_control': '{}{{}} 用于 {} 级别的动态生成'
    }


class DocxtplValidator:
    """Main validator class for docxtpl templates."""

    def __init__(self, report_path: str = "docxtpl_validation_report.md", language: str = "en"):
        self.report_path = Path(report_path)
        self.issues: List[TemplateIssue] = []
        self.jinja_env = Environment()
        self.language = language.lower()
        self.strings = LanguageStrings.ZH if self.language == 'zh' else LanguageStrings.EN
        self.full_content = {}  # Store full content for context extraction
        self.setup_logging()

        # Common Jinja2 patterns for docxtpl
        self.jinja_patterns = [
            r'\{\{.*?\}\}',  # Variables
            r'\{\%.*?\%\}',  # Statements
            r'\{\#.*?\#\}',  # Comments
        ]

        # Docxtpl specific patterns and tags
        self.docxtpl_patterns = {
            'image': r'\{\{\s*.*?\s*\|\s*image\s*.*?\}\}',
            'subdoc': r'\{\{\s*subdoc\s*\(.*?\)\s*\}\}',
            'table': r'\{\%\s*for\s+.*?\s+in\s+.*?\s*\%\}.*?\{\%\s*endfor\s*\%\}',
        }

        # Docxtpl specific control prefixes
        self.docxtpl_prefixes = [
            'p',      # Paragraph control {%p jinja2_tag %}
            'tr',     # Table row control {%tr jinja2_tag %}
            'tc',     # Table cell control {%tc jinja2_tag %}
            'r',      # Run control {%r jinja2_tag %}
        ]

        # Docxtpl supported filters
        self.docxtpl_filters = [
            'image',       # Image filter
            'linebreaks',  # Line breaks filter
            'richtext',    # Rich text filter
        ]

    def setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def tr(self, key: str, default: str = None) -> str:
        """Translate a string key, fallback to default or key if not found."""
        return self.strings.get(key, default or key)

    def tr_category(self, category: str) -> str:
        """Translate error category names."""
        # Convert common category names to translation keys
        category_map = {
            'File Access': 'file_access',
            'Template Structure': 'template_structure', 
            'Docxtpl Structure': 'docxtpl_structure',
            'Jinja2 Syntax': 'jinja2_syntax',
            'Template Parsing': 'template_parsing',
            'Bracket Matching': 'bracket_matching',
            'Quote Matching': 'quote_matching',
            'Expression Syntax': 'expression_syntax',
            'Docxtpl Image': 'docxtpl_image',
            'Docxtpl Subdoc': 'docxtpl_subdoc',
            'Docxtpl paragraph control': 'docxtpl_paragraph_control',
            'Docxtpl table row control': 'docxtpl_table_row_control', 
            'Docxtpl table cell control': 'docxtpl_table_cell_control',
            'Docxtpl run control': 'docxtpl_run_control',
            'Code Quality': 'code_quality',
            'Tag Matching': 'tag_matching'
        }
        
        key = category_map.get(category)
        if key:
            return self.tr(key)
        return category  # fallback to original

    def tr_location(self, location: str) -> str:
        """Translate location names."""
        location_map = {
            'Document': 'document',
            'Overall Template': 'overall_template',
            'Template': 'template'
        }
        
        key = location_map.get(location)
        if key:
            return self.tr(key)
        return location  # fallback to original

    def extract_docx_content(self, docx_path: str) -> Dict[str, str]:
        """Extract text content from docx file (excluding XML tags)."""
        content = {}
        try:
            with ZipFile(docx_path, 'r') as docx:
                # Main document
                if 'word/document.xml' in docx.namelist():
                    xml_content = docx.read('word/document.xml').decode('utf-8')
                    content['Document'] = self.extract_text_from_xml(xml_content)
                
                # Header and footer files
                for file in docx.namelist():
                    if file.startswith('word/header') and file.endswith('.xml'):
                        xml_content = docx.read(file).decode('utf-8')
                        content[f'Header({file})'] = self.extract_text_from_xml(xml_content)
                    elif file.startswith('word/footer') and file.endswith('.xml'):
                        xml_content = docx.read(file).decode('utf-8')
                        content[f'Footer({file})'] = self.extract_text_from_xml(xml_content)
        except Exception as e:
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "File Access",
                f"Cannot extract docx content: {str(e)}",
                docx_path
            )

        return content

    def extract_text_from_xml(self, xml_content: str) -> str:
        """Extract plain text content from Word XML, preserving Jinja2 template syntax and paragraph structure."""
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Collect text by paragraphs to preserve line structure
            paragraphs = []
            
            # Find all paragraph elements (w:p)
            for para_elem in root.iter():
                if para_elem.tag.endswith('}p') or para_elem.tag == 'w:p':  # Handle namespaces
                    # Collect all text within this paragraph
                    para_text_parts = []
                    for text_elem in para_elem.iter():
                        if text_elem.tag.endswith('}t') or text_elem.tag == 'w:t':
                            if text_elem.text:
                                para_text_parts.append(text_elem.text)
                    
                    # Join text within paragraph and add to paragraphs list
                    if para_text_parts:
                        para_text = ''.join(para_text_parts)
                        paragraphs.append(para_text)
            
            # If no paragraphs found, fall back to old method
            if not paragraphs:
                text_parts = []
                for elem in root.iter():
                    if elem.tag.endswith('}t') or elem.tag == 'w:t':
                        if elem.text:
                            text_parts.append(elem.text)
                full_text = ''.join(text_parts)
            else:
                # Join paragraphs with newlines to preserve document structure
                full_text = '\n'.join(paragraphs)
            
            # Fix Jinja2 tags split by Word
            full_text = self.reconstruct_split_jinja_tags(full_text)
            
            # Clean extra whitespace but preserve paragraph breaks
            # Replace multiple consecutive spaces with single space within lines
            lines = full_text.split('\n')
            cleaned_lines = []
            for line in lines:
                # Clean spaces within line but preserve the line structure
                cleaned_line = re.sub(r'[ \t]+', ' ', line.strip())
                if cleaned_line:  # Only add non-empty lines
                    cleaned_lines.append(cleaned_line)
            
            return '\n'.join(cleaned_lines)
        except ET.ParseError as e:
            self.logger.warning("XML parsing error, using raw content: %s", str(e))
            return xml_content
        except Exception as e:  # pylint: disable=broad-except
            self.logger.warning("Text extraction error, using raw content: %s", str(e))
            return xml_content

    def reconstruct_split_jinja_tags(self, text: str) -> str:
        """Reconstruct Jinja2 tags split by Word"""
        # Temporary replacement strategy: reorganize possible split patterns
        # Pattern 1: {{ variable }} split
        text = re.sub(r'\{\{\s*([^}]*?)\s*\}\}', r'{{ \1 }}', text, flags=re.DOTALL)
        
        # Pattern 2: {% statement %} split
        text = re.sub(r'\{\%\s*([^%]*?)\s*\%\}', r'{% \1 %}', text, flags=re.DOTALL)
        
        # Pattern 3: {# comment #} split
        text = re.sub(r'\{\#\s*([^#]*?)\s*\#\}', r'{# \1 #}', text, flags=re.DOTALL)
        
        # Check incomplete tags (main issue)
        issues_found = []
        
        # Check mismatched open tags
        open_var = text.count('{{')
        close_var = text.count('}}')
        if open_var != close_var:
            issues_found.append(f"Variable tag mismatch: {open_var} '{{{{' vs {close_var} '}}}}'")
            
        open_stmt = text.count('{%')
        close_stmt = text.count('%}')
        if open_stmt != close_stmt:
            issues_found.append(f"Statement tag mismatch: {open_stmt} '{{%' vs {close_stmt} '%}}'")
            
        open_comment = text.count('{#')
        close_comment = text.count('#}')
        if open_comment != close_comment:
            issues_found.append(f"Comment tag mismatch: {open_comment} '{{#' vs {close_comment} '#}}'")
        
        # Check incomplete variable tags (like "{{ variable" missing closing)
        incomplete_var_start = re.findall(r'\{\{[^}]*$', text, re.MULTILINE)
        incomplete_var_end = re.findall(r'^[^{]*\}\}', text, re.MULTILINE)
        
        if incomplete_var_start:
            issues_found.append(f"Found {len(incomplete_var_start)} incomplete variable tag starts")
            
        if incomplete_var_end:
            issues_found.append(f"Found {len(incomplete_var_end)} incomplete variable tag ends")
        
        # Check incomplete statement tags
        incomplete_stmt_start = re.findall(r'\{\%[^%]*$', text, re.MULTILINE)
        incomplete_stmt_end = re.findall(r'^[^{]*\%\}', text, re.MULTILINE)
        
        if incomplete_stmt_start:
            issues_found.append(f"Found {len(incomplete_stmt_start)} incomplete statement tag starts")
            
        if incomplete_stmt_end:
            issues_found.append(f"Found {len(incomplete_stmt_end)} incomplete statement tag ends")
        
        # If mismatches found, record to issues list
        for issue in issues_found:
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "Tag Matching",
                issue,
                "Document",
                0,
                "Check if Jinja2 tags in Word document are accidentally split or corrupted. Avoid splitting {{}} tags when editing in Word"
            )
        
        return text

    def find_jinja_blocks(self, text: str) -> List[Tuple[str, int, int]]:
        """Find all Jinja2 blocks and their positions in text, removing duplicates."""
        blocks = []
        seen_blocks = set()  # For deduplication
        
        for pattern in self.jinja_patterns:
            for match in re.finditer(pattern, text, re.DOTALL):
                # Calculate line number
                line_num = text[:match.start()].count('\n') + 1
                block_content = match.group().strip()
                
                # Create unique identifier for deduplication
                block_id = (block_content, line_num, match.start())
                if block_id not in seen_blocks:
                    seen_blocks.add(block_id)
                    blocks.append((block_content, line_num, match.start()))
        
        return sorted(blocks, key=lambda x: x[2])  # Sort by position

    def validate_jinja_syntax(self, template_text: str, location: str):
        """Validate Jinja2 syntax in template text, including docxtpl specific syntax."""
        try:
            # Preprocessing: Replace docxtpl specific tags with standard Jinja2 syntax for validation
            processed_text = self.preprocess_docxtpl_syntax(template_text)
            
            # Try to parse processed template
            self.jinja_env.parse(processed_text)
            
        except TemplateSyntaxError as e:
            # Check if error is caused by docxtpl specific syntax
            if self.is_docxtpl_syntax_error(str(e), template_text):
                return  # This is normal docxtpl syntax, don't report error
                
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "Jinja2 Syntax",
                f"Syntax error: {e.message}",
                location,
                e.lineno if hasattr(e, 'lineno') else 0,
                "Check Jinja2 or docxtpl syntax documentation for correct format"
            )
            
        except Exception as e:
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "Template Parsing",
                f"Template parsing error: {str(e)}",
                location
            )

    def preprocess_docxtpl_syntax(self, text: str) -> str:
        """Preprocess docxtpl specific syntax, converting to standard Jinja2 syntax for validation."""
        processed = text
        
        # Convert docxtpl prefix tags to standard Jinja2 tags
        for prefix in self.docxtpl_prefixes:
            # Match patterns like {%p if condition %}, {% p if condition %}, {%tr for item in items %} etc.
            # Convert them to standard {%if condition %}, {%for item in items %}
            pattern = rf'\{{\%\s*{prefix}\s+(.*?)\s*\%\}}'
            processed = re.sub(pattern, r'{% \1 %}', processed)
        
        return processed

    def is_docxtpl_syntax_error(self, error_msg: str, original_text: str) -> bool:
        """Check if error is caused by docxtpl specific syntax."""
        # Check if contains docxtpl prefixes
        for prefix in self.docxtpl_prefixes:
            pattern = rf'\{{\%\s*{prefix}\s+'
            if re.search(pattern, original_text) and ('unexpected' in error_msg.lower() or 'unknown' in error_msg.lower()):
                return True
        return False

    def validate_individual_blocks(self, text: str, location: str):
        """Validate individual Jinja2 blocks."""
        blocks = self.find_jinja_blocks(text)
        
        for block_text, line_num, _ in blocks:
            self.validate_single_block(block_text, location, line_num)

    def validate_single_block(self, block: str, location: str, line_num: int):
        """Validate a single Jinja2 block."""
        block = block.strip()
        
        # Check common issues
        self.check_bracket_balance(block, location, line_num)
        self.check_quote_balance(block, location, line_num)
        self.check_common_mistakes(block, location, line_num)
        self.check_docxtpl_specific(block, location, line_num)

    def check_bracket_balance(self, block: str, location: str, line_num: int):
        """Check if brackets are properly matched."""
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for char in block:
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    self.add_issue(
                        TemplateIssue.SEVERITY_ERROR,
                        "Bracket Matching",
                        f"Unmatched closing bracket '{char}'",
                        location,
                        line_num,
                        "Ensure all opening brackets have corresponding closing brackets"
                    )
                    return
                expected = brackets[stack.pop()]
                if char != expected:
                    self.add_issue(
                        TemplateIssue.SEVERITY_ERROR,
                        "Bracket Matching",
                        f"Bracket mismatch: expected '{expected}', found '{char}'",
                        location,
                        line_num,
                        "Check bracket pairing"
                    )
                    return
        
        if stack:
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "Bracket Matching",
                f"Unclosed brackets: {', '.join(stack)}",
                location,
                line_num,
                "Close all open brackets"
            )

    def check_quote_balance(self, block: str, location: str, line_num: int):
        """Check if quotes are properly matched."""
        single_quotes = block.count("'")
        double_quotes = block.count('"')
        
        if single_quotes % 2 != 0:
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "Quote Matching",
                "Unmatched single quotes",
                location,
                line_num,
                "Ensure all single quotes are properly paired"
            )
        
        if double_quotes % 2 != 0:
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "Quote Matching",
                "Unmatched double quotes",
                location,
                line_num,
                "Ensure all double quotes are properly paired"
            )

    def check_common_mistakes(self, _block: str, location: str, line_num: int):
        """Check common Jinja2 and docxtpl mistakes."""
        # Check assignment in expressions
        if '{{' in _block and '=' in _block and not any(op in _block for op in ['==', '!=', '<=', '>=', '+=', '-=', '*=', '/=']):
            # Ensure this is actually an assignment and not a comparison
            if re.search(r'\{\{[^}]*[^=!<>]=(?!=)[^}]*\}\}', _block):
                self.add_issue(
                    TemplateIssue.SEVERITY_WARNING,
                    "Expression Syntax",
                    "Assignment (=) found in expression block. Use {% set %} for assignments",
                    location,
                    line_num,
                    "Use {% set variable = value %} for variable assignment"
                )

    def check_docxtpl_specific(self, block: str, location: str, line_num: int):
        """Check docxtpl specific issues and syntax."""
        # Check image filter usage
        if '|' in block and 'image' in block:
            if not re.search(r'\|\s*image\s*(\([^)]*\))?\s*\}\}', block):
                self.add_issue(
                    TemplateIssue.SEVERITY_WARNING,
                    "Docxtpl Image",
                    "Possible incorrect image filter syntax",
                    location,
                    line_num,
                    "Use format: {{ image_var|image }} or {{ image_var|image('width', 'height') }}"
                )
        
        # Check subdoc usage
        if 'subdoc' in block:
            if not re.search(r'subdoc\s*\([^)]+\)', block):
                self.add_issue(
                    TemplateIssue.SEVERITY_WARNING,
                    "Docxtpl Subdoc",
                    "Possible incorrect subdoc syntax",
                    location,
                    line_num,
                    "Use format: {{ subdoc(template_var) }}"
                )
        
        # Check docxtpl prefix tags correct usage
        for prefix in self.docxtpl_prefixes:
            prefix_pattern = rf'\{{\%\s*{prefix}\s+.*?\s*\%\}}'
            if re.search(prefix_pattern, block):
                self.validate_docxtpl_prefix(block, prefix, location, line_num)

    def validate_docxtpl_prefix(self, block: str, prefix: str, location: str, line_num: int):
        """Validate docxtpl prefix tag syntax."""
        prefix_descriptions = {
            'p': "paragraph control",
            'tr': "table row control", 
            'tc': "table cell control",
            'r': "run control"
        }
        
        # Create localized messages
        control_desc = prefix_descriptions.get(prefix, 'control')
        if self.language == 'zh':
            control_desc_zh = {'paragraph control': '段落控制', 'table row control': '表格行控制', 
                              'table cell control': '表格单元格控制', 'run control': '运行控制'}.get(control_desc, control_desc)
            category = f"Docxtpl {control_desc_zh}"
            message = f"使用 {prefix} 前缀进行{control_desc_zh}"
            suggestion = f"{{%{prefix} jinja2_tag %}} 用于{control_desc_zh}级别的动态生成"
        else:
            category = f"Docxtpl {control_desc}"
            message = f"Using {prefix} prefix for {control_desc}"
            suggestion = f"{{%{prefix} jinja2_tag %}} is used for {control_desc} level dynamic generation"
            
        self.add_issue(
            TemplateIssue.SEVERITY_INFO,
            category,
            message,
            location,
            line_num,
            suggestion
        )

    def find_tag_line_numbers(self, text: str, pattern: str) -> List[Tuple[str, int]]:
        """Find all matches of a pattern and their line numbers."""
        matches = []
        for match in re.finditer(pattern, text):
            line_num = text[:match.start()].count('\n') + 1
            matches.append((match.group(), line_num))
        return matches
    
    def find_location_for_line(self, content: Dict[str, str], target_line: int) -> str:
        """Find which document section contains the target line number."""
        current_line = 1
        for location, text in content.items():
            lines_in_section = text.count('\n') + 1
            if current_line <= target_line < current_line + lines_in_section:
                return location
            current_line += lines_in_section
        return "Document"  # fallback

    def find_unmatched_tag_location(self, content: Dict[str, str], all_text: str, 
                                    start_matches: List[Tuple[str, int]], 
                                    end_matches: List[Tuple[str, int]], 
                                    start_tag_name: str, end_tag_name: str) -> Tuple[int, str]:
        """Find the location of the actual unmatched tag by simulating proper nesting."""
        # If we have more starts than ends, find the unmatched start
        if len(start_matches) > len(end_matches):
            # Use stack to match pairs and find unmatched starts
            stack = []
            all_tags = []
            
            # Combine and sort all tags by line number
            for tag, line in start_matches:
                all_tags.append(('start', line, tag))
            for tag, line in end_matches:
                all_tags.append(('end', line, tag))
            all_tags.sort(key=lambda x: x[1])
            
            # Find unmatched start tags
            for tag_type, line_num, tag_text in all_tags:
                if tag_type == 'start':
                    stack.append(line_num)
                elif tag_type == 'end' and stack:
                    stack.pop()
            
            # Return the line of the first unmatched start tag
            if stack:
                error_line = stack[0]
                error_location = self.find_location_for_line(content, error_line)
                return error_line, error_location
        
        # If we have more ends than starts, find the unmatched end
        elif len(end_matches) > len(start_matches):
            # Find the last end tag that doesn't have a matching start
            if end_matches:
                error_line = end_matches[-1][1]  # Last unmatched end
                error_location = self.find_location_for_line(content, error_line)
                return error_line, error_location
        
        # Fallback: use first available tag
        if start_matches:
            error_line = start_matches[0][1]
            error_location = self.find_location_for_line(content, error_line)
            return error_line, error_location
        elif end_matches:
            error_line = end_matches[0][1]
            error_location = self.find_location_for_line(content, error_line)
            return error_line, error_location
        
        return 1, "Document"

    def check_template_structure(self, content: Dict[str, str]):
        """Check overall template structure, including docxtpl prefix tags."""
        all_text = '\n'.join(content.values())
        
        structure_errors = False
        
        # Check standard Jinja2 control structures (without docxtpl prefixes)
        for control_type in ['if', 'for', 'with', 'block']:
            # Match standard control structures without prefixes, excluding docxtpl prefixes
            start_pattern = rf'\{{\%\s*(?!(?:p|tr|tc|r)\s+){control_type}\b.*?\%\}}'
            end_type = 'end' + control_type
            end_pattern = rf'\{{\%\s*(?!(?:p|tr|tc|r)\s+){end_type}\s*\%\}}'
            
            start_matches = self.find_tag_line_numbers(all_text, start_pattern)
            end_matches = self.find_tag_line_numbers(all_text, end_pattern)
            
            # Check exact matching
            if len(start_matches) != len(end_matches):
                # Find the actual problematic location by analyzing unmatched tags
                error_line, error_location = self.find_unmatched_tag_location(
                    content, all_text, start_matches, end_matches, f"{{% {control_type} %}}", f"{{% {end_type} %}}"
                )
                
                self.add_issue(
                    TemplateIssue.SEVERITY_ERROR,
                    "Template Structure",
                    f"Standard {control_type} control structure mismatch: {len(start_matches)} start tags, {len(end_matches)} end tags",
                    error_location,
                    error_line,
                    f"Ensure all {{% {control_type} %}} have corresponding {{% {end_type} %}}"
                )
                structure_errors = True
        
        # Check docxtpl prefix control structures
        for prefix in self.docxtpl_prefixes:
            for control_type in ['if', 'for', 'with', 'block']:
                start_pattern = rf'\{{\%\s*{prefix}\s+{control_type}\b.*?\%\}}'
                end_type = 'end' + control_type
                end_pattern = rf'\{{\%\s*{prefix}\s+{end_type}\s*\%\}}'
                
                start_matches = self.find_tag_line_numbers(all_text, start_pattern)
                end_matches = self.find_tag_line_numbers(all_text, end_pattern)
                
                # Also check for improperly formatted end tags (missing prefix)
                wrong_end_pattern1 = rf'\{{\%\s*{end_type}\s*\%\}}'  # e.g., {% endif %} instead of {% p endif %}
                wrong_end_pattern2 = rf'\{{\%\s*end\s+{control_type}\s*\%\}}'  # e.g., {% end if %} instead of {% p end if %}
                wrong_end_matches1 = self.find_tag_line_numbers(all_text, wrong_end_pattern1)
                wrong_end_matches2 = self.find_tag_line_numbers(all_text, wrong_end_pattern2)
                wrong_end_matches = wrong_end_matches1 + wrong_end_matches2
                
                if len(start_matches) != len(end_matches):
                    # Check if there are wrong format end tags that should have the prefix
                    if wrong_end_matches:
                        # Report the wrong format tag as the error
                        error_line = wrong_end_matches[0][1]
                        error_location = self.find_location_for_line(content, error_line)
                        
                        # Create localized error message and suggestion
                        if self.language == 'zh':
                            error_msg = f"{{%{prefix} {control_type}%}} 标签不匹配：发现 {{%{end_type}%}} 而不是 {{%{prefix} {end_type}%}}"
                            suggestion = f"将 {{%{end_type}%}} 更改为 {{%{prefix} {end_type}%}} 以匹配 docxtpl 前缀模式"
                        else:
                            error_msg = f"{{%{prefix} {control_type}%}} tag mismatch: found {{%{end_type}%}} instead of {{%{prefix} {end_type}%}}"
                            suggestion = f"Change {{%{end_type}%}} to {{%{prefix} {end_type}%}} to match the docxtpl prefix pattern"
                        
                        self.add_issue(
                            TemplateIssue.SEVERITY_ERROR,
                            "Docxtpl Structure",
                            error_msg,
                            error_location,
                            error_line,
                            suggestion
                        )
                    else:
                        # Find the actual problematic location by analyzing unmatched tags
                        error_line, error_location = self.find_unmatched_tag_location(
                            content, all_text, start_matches, end_matches, f"{{%{prefix} {control_type}%}}", f"{{%{prefix} {end_type}%}}"
                        )
                        
                        self.add_issue(
                            TemplateIssue.SEVERITY_ERROR,
                            "Docxtpl Structure",
                            f"{{%{prefix} {control_type}%}} tag mismatch: {len(start_matches)} start, {len(end_matches)} end",
                            error_location,
                            error_line,
                            f"Ensure all {{%{prefix} {control_type}%}} have corresponding {{%{prefix} {end_type}%}}"
                        )
                    structure_errors = True
        
        if not structure_errors:
            self.logger.info("Template structure check passed, all control structures are well-matched")

    def analyze_template_quality(self, content: Dict[str, str]):
        """Analyze template quality and improvement suggestions."""
        all_text = '\n'.join(content.values())
        
        # Check hardcoded values
        hardcoded_strings = re.findall(r'\{\{\s*["\'][^"\']+["\']\s*\}\}', all_text)
        hardcoded_numbers = re.findall(r'\{\{\s*\d+\s*\}\}', all_text)
        
        if hardcoded_strings:
            self.add_issue(
                TemplateIssue.SEVERITY_INFO,
                "Code Quality",
                f"Hardcoded strings found in template: {len(hardcoded_strings)} occurrences",
                "Template",
                0,
                "Consider using variables instead of hardcoded values to improve template flexibility"
            )
        
        if hardcoded_numbers:
            self.add_issue(
                TemplateIssue.SEVERITY_INFO,
                "Code Quality",
                f"Hardcoded numbers found in template: {len(hardcoded_numbers)} occurrences",
                "Template",
                0,
                "Consider using variables instead of hardcoded numbers"
            )
        
        # Check complex expressions
        complex_expr = re.findall(r'\{\{[^}]{50,}\}\}', all_text)
        if complex_expr:
            self.add_issue(
                TemplateIssue.SEVERITY_INFO,
                "Code Quality",
                f"Complex expressions found: {len(complex_expr)} occurrences",
                "Template",
                0,
                "Consider breaking complex expressions into simpler parts or using {% set %}"
            )

    def extract_context(self, location: str, line_number: int, context_lines: int = 2) -> str:
        """Extract context around the error location."""
        if not self.full_content:
            return ""
        
        # If location is specific (like "Document"), use that section
        if location in self.full_content:
            text = self.full_content[location]
            lines = text.split('\n')
        else:
            # For overall template errors, use combined content
            combined_text = '\n'.join(self.full_content.values())
            lines = combined_text.split('\n')
        
        if line_number <= 0 or line_number > len(lines):
            return ""
        
        start_line = max(0, line_number - context_lines - 1)
        end_line = min(len(lines), line_number + context_lines)
        
        context_lines_list = []
        for i in range(start_line, end_line):
            line_marker = ">>> " if i == line_number - 1 else "    "
            context_lines_list.append(f"{line_marker}{i+1}: {lines[i]}")
        
        return "\n".join(context_lines_list)

    def add_issue(self, severity: str, category: str, message: str, 
                  location: str = "", line_number: int = 0, suggestion: str = ""):
        """Add issue to list, avoiding duplicates."""
        # Check if same issue already exists
        for existing_issue in self.issues:
            if (existing_issue.severity == severity and
                existing_issue.category == category and
                existing_issue.message == message and
                existing_issue.location == location and
                existing_issue.line_number == line_number):
                return  # Same issue exists, don't add duplicate
        
        # Extract context for the issue
        context = self.extract_context(location, line_number) if line_number > 0 else ""
        
        issue = TemplateIssue(severity, category, message, location, line_number, suggestion, context)
        self.issues.append(issue)
        
        # Log important issues to console
        if severity == TemplateIssue.SEVERITY_ERROR:
            self.logger.error(f"{location}:{line_number} - {message}")
        elif severity == TemplateIssue.SEVERITY_WARNING:
            self.logger.warning(f"{location}:{line_number} - {message}")

    def validate_template(self, docx_path: str):
        """Main validation method."""
        self.logger.info(self.strings['validation_starting'].format(docx_path))
        
        if not Path(docx_path).exists():
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "File Access",
                f"Template file not found: {docx_path}",
                docx_path
            )
            return
        
        # Extract content
        content = self.extract_docx_content(docx_path)
        self.full_content = content  # Store for context extraction
        
        if not content:
            self.add_issue(
                TemplateIssue.SEVERITY_ERROR,
                "File Access",
                "Cannot extract any content from template",
                docx_path
            )
            return
        
        # Validate each section
        for location, text in content.items():
            self.validate_jinja_syntax(text, location)
            self.validate_individual_blocks(text, location)
        
        # Check overall structure
        self.check_template_structure(content)
        
        # Analyze quality
        self.analyze_template_quality(content)
        
        self.logger.info(self.strings['validation_complete'].format(len(self.issues)))

    def generate_report(self):
        """Generate detailed markdown report."""
        self.logger.info(self.strings['generating_report'].format(self.report_path))
        
        # Group issues by severity
        errors = [i for i in self.issues if i.severity == TemplateIssue.SEVERITY_ERROR]
        warnings = [i for i in self.issues if i.severity == TemplateIssue.SEVERITY_WARNING]
        info = [i for i in self.issues if i.severity == TemplateIssue.SEVERITY_INFO]
        
        with open(self.report_path, 'w', encoding='utf-8') as f:
            f.write(f"# {self.strings['report_title']}\n\n")
            f.write(f"**{self.strings['generated']}:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Summary
            f.write(f"## {self.strings['summary']}\n\n")
            f.write(f"- **{self.strings['total_issues']}:** {len(self.issues)}\n")
            f.write(f"- **{self.strings['errors']}:** {len(errors)} 🔴\n")
            f.write(f"- **{self.strings['warnings']}:** {len(warnings)} 🟡\n")
            f.write(f"- **{self.strings['info']}/{self.strings['suggestion'].replace('💡 ', '')}:** {len(info)} 🔵\n\n")
            
            # Write issues by severity
            self.write_issues_section(f, self.strings['errors'], errors, "🔴")
            self.write_issues_section(f, self.strings['warnings'], warnings, "🟡")
            self.write_issues_section(f, f"{self.strings['info']} & {self.strings['suggestion'].replace('💡 ', '')}", info, "🔵")
            
            # Best practices
            f.write("## Docxtpl Template Best Practices\n\n")
            f.write("### Basic Syntax\n")
            f.write("1. **Variables:** Use `{{ variable_name }}` for simple variable substitution\n")
            f.write("2. **Images:** Use `{{ image_var|image }}` or `{{ image_var|image('width', 'height') }}`\n")
            f.write("3. **Subdocs:** Use `{{ subdoc(template_var) }}` to include other templates\n")
            f.write("4. **Loops:** Always close `{% for %}` with `{% endfor %}`\n")
            f.write("5. **Conditionals:** Always close `{% if %}` with `{% endif %}`\n")
            f.write("6. **Complex Logic:** Use `{% set %}` to assign complex expressions to variables\n\n")
            
            f.write("### Docxtpl Specific Prefix Tags\n")
            f.write("7. **Paragraph Control:** Use `{% p if condition %}...{% p endif %}` for paragraph-level dynamic generation\n")
            f.write("8. **Table Rows:** Use `{% tr for item in items %}...{% tr endfor %}` for table row-level dynamic generation\n")
            f.write("9. **Table Cells:** Use `{% tc if condition %}...{% tc endif %}` for cell-level dynamic generation\n")
            f.write("10. **Run Control:** Use `{% r if condition %}...{% r endif %}` for text run-level dynamic generation\n\n")
            
            f.write("### Filters\n")
            f.write("11. **Rich Text:** Use `{{ variable|richtext }}` to preserve text formatting\n")
            f.write("12. **Line Breaks:** Use `{{ variable|linebreaks }}` to handle line breaks\n\n")
            
            f.write("### Examples\n")
            f.write("```jinja2\n")
            f.write("# Paragraph control\n")
            f.write("{% p if display_paragraph %}\n")
            f.write("One or more paragraphs\n")
            f.write("{% p endif %}\n\n")
            f.write("# Table structure\n")
            f.write("{% tr for row in table_data %}\n")
            f.write("  {% tc for cell in row %}\n")
            f.write("    {{ cell }}\n")
            f.write("  {% tc endfor %}\n")
            f.write("{% tr endfor %}\n\n")
            f.write("# Run control\n")
            f.write("{% r if show_text %}\n")
            f.write("Text run content\n")
            f.write("{% r endif %}\n")
            f.write("```\n\n")
        
        self.logger.info(self.strings['report_generated'])

    def write_issues_section(self, f, title: str, issues: List[TemplateIssue], icon: str):
        """Write issues section to report file."""
        if not issues:
            f.write(f"## {title} {icon}\n\n")
            f.write(f"{self.strings['no_issues']}\n\n")
            return
            
        f.write(f"## {title} {icon}\n\n")
        
        # Group by category
        categories = {}
        for issue in issues:
            if issue.category not in categories:
                categories[issue.category] = []
            categories[issue.category].append(issue)
        
        for category, cat_issues in categories.items():
            translated_category = self.tr_category(category)
            f.write(f"### {translated_category}\n\n")
            
            for i, issue in enumerate(cat_issues, 1):
                f.write(f"#### {i}. {issue.message}\n\n")
                
                if issue.location:
                    translated_location = self.tr_location(issue.location)
                    f.write(f"**{self.strings['location']}:** {translated_location}")
                    if issue.line_number > 0:
                        f.write(f" ({self.strings['line']} {issue.line_number})")
                    f.write("\n\n")
                
                if issue.context:
                    f.write(f"**{self.strings['context']}:**\n```\n{issue.context}\n```\n\n")
                
                if issue.suggestion:
                    f.write(f"**{self.strings['suggestion']}:** {issue.suggestion}\n\n")
                
                if i < len(cat_issues):
                    f.write("---\n\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate docxtpl Word template Jinja2 syntax errors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python docxtpl_checker.py template.docx
  python docxtpl_checker.py template.docx --report custom_report.md
  python docxtpl_checker.py template.docx --report /path/to/report.md
        """
    )
    
    parser.add_argument(
        'template',
        help='docxtpl template file path (.docx)'
    )
    
    parser.add_argument(
        '--report', '-r',
        default='docxtpl_validation_report.md',
        help='Validation report output path (default: docxtpl_validation_report.md in current directory)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--language', '-l',
        choices=['en', 'zh'],
        default='en',
        help='Output language: en (English) or zh (Chinese) (default: en)'
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate template
    validator = DocxtplValidator(args.report, args.language)
    validator.validate_template(args.template)
    
    # Print minimal info to terminal
    errors = [i for i in validator.issues if i.severity == TemplateIssue.SEVERITY_ERROR]
    warnings = [i for i in validator.issues if i.severity == TemplateIssue.SEVERITY_WARNING]
    info = [i for i in validator.issues if i.severity == TemplateIssue.SEVERITY_INFO]
    
    print(f"\n{validator.strings['validation_results']}")
    print(f"  {validator.strings['errors']}: {len(errors)}")
    print(f"  {validator.strings['warnings']}: {len(warnings)}")
    print(f"  {validator.strings['info']}: {len(info)}")
    
    # Generate report if requested or if there are issues
    if args.report or validator.issues:
        validator.generate_report()
        print(f"\n{validator.strings['detailed_report_saved'].format(validator.report_path)}")
    
    # Exit with error code if errors found
    if errors:
        print(f"\n{validator.strings['validation_failed'].format(len(errors))}")
        sys.exit(1)
    else:
        if warnings:
            print(f"\n{validator.strings['validation_warnings'].format(len(warnings))}")
        else:
            print(f"\n{validator.strings['validation_passed']}")
        sys.exit(0)


if __name__ == "__main__":
    main()