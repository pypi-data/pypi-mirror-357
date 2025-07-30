import re
import html
from typing import Dict, Any, Optional
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer, guess_lexer
from .base import Plugin
from ..utils.logging import get_logger

# Get logger using the centralized logging system
logger = get_logger("plugins.syntax_highlight")


class SyntaxHighlightPlugin(Plugin):
    """Plugin for syntax highlighting code blocks in content."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        linenums = self.config.get('linenums', False)

        style = self.config.get('style', 'monokai')
        if (hasattr(self, 'engine') and self.engine 
                and hasattr(self.engine, 'config')):
            syntax_config = self.engine.config.get("syntax_highlight", {})
            style = syntax_config.get("style", style)
        
        # Create formatter with explicit settings for whitespace
        self.formatter = HtmlFormatter(
            style=style,
            cssclass=self.config.get('css_class', 'highlight'),
            linenos=linenums,
            noclasses=False,
            tabsize=4,
            # Critical settings for preserving whitespace
            prestyles="white-space: pre !important; tab-size: 4 !important;",
            nobackground=True,
            wrapcode=True,  # Wrap code in additional div for better control
            nowrap=False,   # Allow long lines to wrap
        )
        
    def _detect_language_from_code(self, code):
        """Detect language from code content."""
        # Common language patterns
        patterns = {
            'python': (
                r'\bdef\s+\w+\s*\(', r'\bclass\s+\w+\s*\(', 
                r'\bimport\s+\w+', r'\bprint\s*\('
            ),
            'javascript': (
                r'\bfunction\s+\w+\s*\(', r'\bconst\s+\w+\s*=', 
                r'\blet\s+\w+\s*=', r'\bvar\s+\w+\s*='
            ),
            'html': (
                r'<html.*?>', r'<div.*?>', r'<body.*?>', r'<script.*?>'
            ),
            'css': (
                r'\.\w+\s*{', r'#\w+\s*{', r'@media\s+', r'body\s*{'
            ),
            'java': (
                r'\bpublic\s+class\s+\w+', r'\bprivate\s+\w+\s+\w+', 
                r'\bprotected\s+\w+\s+\w+', r'\bimport\s+java\.'
            ),
            'ruby': (
                r'\bdef\s+\w+\s*\n', r'\bclass\s+\w+\s*\n', 
                r'\bmodule\s+\w+\s*\n', r'\brequire\s+[\'""]'
            ),
            'php': (
                r'<\?php', r'\bfunction\s+\w+\s*\(', 
                r'\$\w+\s*=', r'\becho\s+'
            ),
            'c': (
                r'\bint\s+\w+\s*\(', r'\bvoid\s+\w+\s*\(', 
                r'#include\s+<\w+\.h>', r'\bstruct\s+\w+\s*{'
            ),
            'cpp': (
                r'#include\s+<\w+>', r'\bclass\s+\w+\s*{', 
                r'\bnamespace\s+\w+', r'\btemplate\s*<'
            ),
            'go': (
                r'\bfunc\s+\w+\s*\(', r'\bpackage\s+\w+', 
                r'\bimport\s+\(', r'\btype\s+\w+\s+struct\s+{'
            ),
            'rust': (
                r'\bfn\s+\w+\s*\(', r'\buse\s+\w+', 
                r'\bstruct\s+\w+', r'\benum\s+\w+'
            ),
            'typescript': (
                r'\binterface\s+\w+', r'\btype\s+\w+\s*=', 
                r'\bclass\s+\w+\s*{', r'\bfunction\s+\w+<'
            ),
            'swift': (
                r'\bfunc\s+\w+\s*\(', r'\bclass\s+\w+', 
                r'\bvar\s+\w+\s*:', r'\blet\s+\w+\s*:'
            ),
            'kotlin': (
                r'\bfun\s+\w+\s*\(', r'\bclass\s+\w+', 
                r'\bvar\s+\w+\s*:', r'\bval\s+\w+\s*:'
            ),
            'csharp': (
                r'\bpublic\s+class\s+\w+', r'\bprivate\s+\w+\s+\w+', 
                r'\bnamespace\s+\w+', r'\busing\s+\w+;'
            )
        }
        
        # Check each language patterns
        for lang, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, code):
                    logger.info(f"Detected {lang} from code content")
                    return lang
        
        # Try to guess language automatically with Pygments
        try:
            lexer = guess_lexer(code)
            lang = lexer.aliases[0]
            logger.info(f"Pygments detected language: {lang}")
            return lang
        except Exception:
            logger.info("Failed to detect language, using text")
            return "text"
    
    def _decode_entities(self, content):
        """Decode HTML entities to normal characters."""
        return html.unescape(content)
    
    def _process_code_with_linebreaks(self, code, lexer):
        """Process code with Pygments while preserving line breaks and tabs."""
        # Remember if we have tabs
        has_tabs = '\t' in code
        
        # Save template strings for later restoration
        template_strings = {}
        if hasattr(lexer, 'aliases') and any(
            lang in lexer.aliases for lang in 
            ['js', 'javascript', 'jsx', 'typescript', 'ts', 'tsx',
             'ruby', 'erb', 'php', 'kotlin', 'swift']
        ):
            template_pattern = r'`([^`]*?)[#$]\{([^}]*?)\}([^`]*?)`'
            template_matches = list(re.finditer(template_pattern, code))
            
            for i, match in enumerate(template_matches):
                placeholder = f"__TEMPLATE_STRING_{i}__"
                template_strings[placeholder] = match.group(0)
                code = code.replace(match.group(0), placeholder)
        
        # Get HTML markup from Pygments with basic highlighting
        formatted_html = highlight(code, lexer, self.formatter)
        
        # Process spaces after keywords
        keyword_pattern = r'<span class="(?:k|kd|kc|kr|kt)">(\w+)</span>'
        
        def add_space_after_keyword(m):
            keyword = m.group(1)
            return f'<span class="k">{keyword}</span><span class="w"> </span>'
        
        formatted_html = re.sub(
            keyword_pattern, 
            add_space_after_keyword, 
            formatted_html
        )
        
        # Add spaces around operators
        operator_pattern = r'(<span class="o">[+\-*/=<>!&|^%]+</span>)'
        space_token = '<span class="w"> </span>'
        formatted_html = re.sub(
            operator_pattern, 
            f'{space_token}\\1{space_token}', 
            formatted_html
        )
                
        # Extract content between pre tags
        pattern = r'<pre[^>]*>(.*?)</pre>'
        pre_match = re.search(pattern, formatted_html, re.DOTALL)
        if not pre_match:
            return formatted_html
            
        pre_content = pre_match.group(1)
        
        # Split by lines and add line spans
        lines = pre_content.split('\n')
        processed_lines = []
        
        # Get original lines for comparison
        orig_lines = code.split('\n')
        
        for i, (line, orig_line) in enumerate(zip(lines, orig_lines)):
            # If line is empty, add empty line
            if not orig_line.strip():
                processed_lines.append(
                    f'<span class="line" id="L{i+1}">&nbsp;</span>'
                )
                continue
            
            # Copy indentation from original code
            indent_match = re.match(r'^(\s+)', orig_line)
            if indent_match:
                orig_indent = indent_match.group(1)
                
                # Count tabs and spaces
                tab_count = orig_indent.count('\t')
                space_count = orig_indent.count(' ')
                
                # Create visible indentation
                if tab_count > 0:
                    indent_html = f'<span class="ws" data-tabs="{tab_count}">'
                    
                    indent_chars = []
                    for char in orig_indent:
                        if char == '\t':
                            indent_chars.append('&nbsp;&nbsp;&nbsp;&nbsp;')
                        elif char == ' ':
                            indent_chars.append('&nbsp;')
                    
                    indent_html += ''.join(indent_chars)
                else:
                    indent_html = '<span class="ws">'
                    indent_html += '&nbsp;' * space_count
                
                indent_html += '</span>'
                
                line = re.sub(r'^\s*', indent_html, line)
            
            processed_lines.append(
                f'<span class="line" id="L{i+1}">{line}</span>'
            )
        
        processed_content = '\n'.join(processed_lines)
        
        formatted_html = formatted_html.replace(
            pre_match.group(1), processed_content
        )
        
        # Restore template strings
        if template_strings:
            for placeholder, template in template_strings.items():
                parts = re.match(
                    r'`([^`]*?)[#$]\{([^}]*?)\}([^`]*?)`', 
                    template
                )
                if parts:
                    before, expr, after = parts.groups()
                    template_html = (
                        f'<span class="sb">`{html.escape(before)}'
                        f'${{{expr}}}'
                        f'{html.escape(after)}`</span>'
                    )
                    formatted_html = formatted_html.replace(
                        html.escape(placeholder), template_html
                    )
        
        # Include whitespace in styles
        if 'white-space: pre' not in formatted_html:
            style = 'white-space: pre !important; tab-size: 4 !important;'
            formatted_html = formatted_html.replace(
                '<pre>', f'<pre style="{style}">'
            )
        
        # Add has-tabs class if we have tabs
        if has_tabs:
            formatted_html = formatted_html.replace(
                'class="highlight"', 
                'class="highlight has-tabs"'
            )
            
        return formatted_html
    
    def _get_token_class(self, token_type):
        """Получить CSS-класс для типа токена Pygments."""
        # Преобразуем токен в CSS-класс
        ttype = token_type
        cls = ''
        while ttype:
            if ttype in self.formatter.ttype2class:
                cls = self.formatter.ttype2class[ttype]
                break
            ttype = ttype.parent
        if not cls:
            cls = 'text'  # Значение по умолчанию
        return cls
    
    def process_content(self, content: str) -> str:
        """Process content and highlight code blocks."""
        if not content or len(content) < 10:
            return content

        # Function for highlighting code with tab/newline preservation
        def highlight_block(code, lang):
            try:
                # Decode HTML entities properly
                code = self._decode_entities(code)
                
                try:
                    # Try to get lexer by language
                    lexer = get_lexer_by_name(lang)
                except ValueError:
                    # Try to detect language automatically
                    detected_lang = self._detect_language_from_code(code)
                    lang = detected_lang
                    try:
                        lexer = get_lexer_by_name(lang)
                    except ValueError:
                        lexer = TextLexer()
                
                # Process code with Pygments, preserving tabs and newlines
                html_code = self._process_code_with_linebreaks(code, lexer)
                
                # Create code block with language tag on separate lines
                # for better readability in the output
                result = (
                    '<div class="code-block language-{0}">\n'
                    '    <div class="language-tag">{0}</div>\n'
                    '    {1}\n'
                    '</div>'
                ).format(lang, html_code)
                
                return result
            except Exception as e:
                logger.error(f"Error highlighting code: {e}")
                # Fallback to simple HTML with line breaks
                escaped = html.escape(code)
                return f'<pre><code>{escaped}</code></pre>'
        
        # Process markdown code blocks: ```lang ...code... ```
        def process_md_block(match):
            lang = match.group(1).strip() if match.group(1) else 'text'
            code = match.group(2)
            
            # Особая обработка Mermaid диаграмм
            if lang.lower() == 'mermaid':
                # Преобразуем блок mermaid в div.mermaid
                return f'<div class="mermaid">{code}</div>'
                
            logger.info(f"Processing markdown code block: {lang}")
            return highlight_block(code, lang)
        
        # Find all markdown code blocks
        md_pattern = re.compile(
            r'```\s*([a-zA-Z0-9_+-]+)?\s*\n((?:(?!```).|\n)+?)\s*```',
            re.MULTILINE
        )
        content = md_pattern.sub(process_md_block, content)
        
        # Process HTML code blocks: <pre><code>...</code></pre>
        def process_html_block(match):
            full_match = match.group(0)
            code = match.group(1)
            
            # Look for language in class attribute
            lang_match = re.search(
                r'class=["\'](.*?language-(\w+))["\']', full_match
            )
            
            if lang_match:
                lang = lang_match.group(2)
                # Особая обработка Mermaid диаграмм
                if lang.lower() == 'mermaid':
                    return f'<div class="mermaid">{code}</div>'
            else:
                # Detect language by content
                lang = self._detect_language_from_code(code)
            return highlight_block(code, lang)
        
        # Find HTML code blocks
        html_pattern = re.compile(
            r'<pre>\s*<code.*?>(.*?)</code>\s*</pre>',
            re.DOTALL
        )
        content = html_pattern.sub(process_html_block, content)
        
        # Process inline code: `code`
        content = re.sub(
            r'`([^`\n]+)`',
            lambda m: f'<code class="inline-code">'
                      f'{html.escape(m.group(1))}</code>',
            content
        )
        
        # Fix JavaScript template literals that might still have HTML tags visible
        def fix_js_template_literals(content):
            # Находим блоки JavaScript кода
            js_blocks_pattern = re.compile(
                r'<div class="code-block language-(javascript|js)">.*?</div>',
                re.DOTALL
            )
            
            def fix_template_literal(match):
                block = match.group(0)
                # Проверяем, есть ли в блоке проблемные шаблонные строки
                if 'Loop iteration' in block and '&lt;/span&gt;' in block:
                    # Заменяем неправильно отрендеренные шаблонные литералы
                    block = re.sub(
                        r'<span class="nx"><span class="sb"><code class="inline-code">([^<]+)\${&lt;span class="nx"&gt;([^<]+)&lt;/span&gt;}</code></span></span>',
                        r'<span class="sb">`\1${\2}`</span>',
                        block
                    )
                return block
            
            # Применяем фикс к JavaScript блокам
            return js_blocks_pattern.sub(fix_template_literal, content)
        
        # Применяем фикс для шаблонных строк JavaScript
        content = fix_js_template_literals(content)
        
        return content