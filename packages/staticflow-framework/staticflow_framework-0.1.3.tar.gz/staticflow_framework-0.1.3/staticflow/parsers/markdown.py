from typing import Any, Dict, List, Optional, Union
import markdown
from .base import ContentParser
from staticflow.plugins.syntax_highlight import SyntaxHighlightPlugin
from .extensions.video import makeExtension as makeVideoExtension
from .extensions.audio import makeExtension as makeAudioExtension
from datetime import datetime
import frontmatter
import re


class MarkdownParser(ContentParser):
    """Парсер для Markdown контента."""

    def __init__(
        self,
        extensions: Optional[List[Union[str, Any]]] = None
    ) -> None:
        super().__init__()
        self.extensions: List[Union[str, Any]] = extensions or [
            'fenced_code',
            'tables',
            'toc',
            'meta',
            'attr_list',
            'def_list',
            'footnotes',
            'pymdownx.highlight',
            'pymdownx.superfences',
            'pymdownx.arithmatex',
            'pymdownx.details',
            'pymdownx.emoji',
            'pymdownx.tasklist',
            'pymdownx.critic',
            'pymdownx.mark',
            'pymdownx.smartsymbols',
            'pymdownx.tabbed',
            'pymdownx.arithmatex',
            'pymdownx.betterem',
            'pymdownx.caret',
            'pymdownx.critic',
            'pymdownx.details',
            'pymdownx.emoji',
            'pymdownx.inlinehilite',
            'pymdownx.magiclink',
            'pymdownx.mark',
            'pymdownx.smartsymbols',
            'pymdownx.superfences',
            'pymdownx.tabbed',
            'pymdownx.tasklist',
            'pymdownx.tilde',
            makeVideoExtension(),
            makeAudioExtension(),
        ]
        self.extension_configs: Dict[str, Dict[str, Any]] = {
            'toc': {
                'permalink': True,
                'permalink_class': 'headerlink',
                'toc_depth': 3
            },
            'pymdownx.highlight': {
                'css_class': 'highlight',
                'guess_lang': True,
                'preserve_tabs': True,  # Сохраняем табуляцию
                'use_pygments': True,
                'noclasses': False,
                'linenums': False
            },
            'pymdownx.superfences': {
                'custom_fences': [
                    {
                        'name': 'mermaid',
                        'class': 'mermaid',
                        'format': str
                    }
                ]
            },
            'pymdownx.arithmatex': {
                'generic': True
            },
        }
        self._md: markdown.Markdown = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self.extension_configs
        )
        self.syntax_highlighter: SyntaxHighlightPlugin = (
            SyntaxHighlightPlugin()
        )

    def parse(self, content: str) -> str:
        """Преобразует Markdown в HTML с сохранением табуляции."""
        self._md.reset()
        html: str = self._md.convert(content)

        # Обрабатываем блоки кода для сохранения табуляции
        html = self._preserve_code_tabs(html)

        if self.get_option('syntax_highlight'):
            html = self.syntax_highlighter.process_content(html)

        return html

    def _preserve_code_tabs(self, html: str) -> str:
        """Сохраняет табуляцию в блоках кода."""
        # Находим все блоки кода
        code_block_pattern = r'<pre><code[^>]*>(.*?)</code></pre>'
        
        def process_code_block(match):
            code_content = match.group(1)
            language = ''
            
            # Извлекаем язык из класса
            lang_match = re.search(
                r'class="[^"]*language-([^"\s]+)', 
                match.group(0)
            )
            if lang_match:
                language = lang_match.group(1)
            
            # Сохраняем пробелы и табуляцию
            code_lines = code_content.split('\n')
            processed_lines = []
            
            for line in code_lines:
                # Обрабатываем начальные пробелы
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    # Заменяем пробелы на span с классом w
                    space_spans = '<span class="w"> </span>' * indent
                    line = space_spans + line.lstrip()
                
                # Заменяем все пробельные токены на унифицированный формат
                line = re.sub(
                    r'<span class="w"></span>',
                    '<span class="w"> </span>',
                    line
                )

                # Заменяем все множественные пробелы на токены w
                def repl_ws(m):
                    count = len(m.group(1))
                    return '<span class="w"> </span>' * count
                line = re.sub(
                    r'<span class="w">( +)</span>',
                    repl_ws,
                    line
                )

                # Заменяем все оставшиеся пробелы внутри строки
                line = re.sub(
                    r'<span class="w"></span>',
                    '<span class="w"> </span>',
                    line
                )

                # Заменяем все пробельные последовательности
                whitespace_token = '<span class="w"> </span>'
                line = re.sub(
                    r'<span class="w">\s+</span>',
                    lambda m: whitespace_token * len(m.group()),
                    line
                )
        
                processed_lines.append(line)
            
            code_content = '\n'.join(processed_lines)
            
            # Экранируем HTML-сущности
            code_content = self._escape_html_entities(code_content)
            
            # Добавляем подсветку синтаксиса
            if language and self.get_option('syntax_highlight'):
                highlighted_code = self._highlight_syntax(
                    code_content, 
                    language
                )
                return (
                    f'<pre><code class="language-{language}">'
                    f'{highlighted_code}</code></pre>'
                )
            else:
                return (
                    f'<pre><code class="language-{language}">'
                    f'{code_content}</code></pre>'
                )
        
        return re.sub(
            code_block_pattern, 
            process_code_block, 
            html, 
            flags=re.DOTALL
        )

    def _escape_html_entities(self, content: str) -> str:
        """Экранирует HTML-сущности в коде."""
        # Заменяем специальные символы на HTML-сущности
        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        }
        
        for char, entity in replacements.items():
            content = content.replace(char, entity)
        
        return content

    def _highlight_syntax(self, code: str, language: str) -> str:
        """Добавляет подсветку синтаксиса к коду."""
        try:
            # Используем Pygments для подсветки синтаксиса
            from pygments import highlight
            from pygments.lexers import get_lexer_by_name
            from pygments.formatters import HtmlFormatter
            from pygments.token import Token
            from pygments.util import ClassNotFound
            
            try:
                lexer = get_lexer_by_name(language, stripall=False)
            except ClassNotFound:
                # Если лексер не найден, используем текстовый
                lexer = get_lexer_by_name('text', stripall=False)
            
            class TokenFormatter(HtmlFormatter):
                def __init__(self, **options):
                    super().__init__(**options)
                    # Используем стандартные типы токенов Pygments
                    self.token_styles = {}  # Не переопределяем стили

                def _get_css_class(self, ttype):
                    """Используем стандартные классы Pygments"""
                    return super()._get_css_class(ttype)

                def wrap(self, source, outfile):
                    """Обрабатываем токены"""
                    for i, (token_type, value) in enumerate(source):
                        if token_type == Token.Text and value.isspace():
                            # Обрабатываем пробельные символы
                            for char in value:
                                if char == ' ':
                                    # Используем стандартный класс w
                                    yield Token.Text.Whitespace, ' '
                                elif char == '\t':
                                    # Для табуляции используем 4 пробела
                                    yield Token.Text.Whitespace, '    '
                                elif char == '\n':
                                    # Для переноса строки
                                    yield Token.Text, '\n'
                        else:
                            yield token_type, value

            formatter = TokenFormatter(
                style='monokai',
                noclasses=False,
                cssclass='highlight',
                linenos=False,
                nowrap=True,
                wrapcode=True,
                nobackground=True
            )

            highlighted = highlight(code, lexer, formatter)

            # Заменяем все оставшиеся пробелы на унифицированный формат
            highlighted = re.sub(
                r'<span class="w"></span>',
                '<span class="w"> </span>',
                highlighted
            )
            
            return highlighted
            
        except Exception:
            # Если подсветка не удалась, возвращаем исходный код
            # с сохранением форматирования
            return code

    def add_extension(
        self,
        extension: str,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Добавляет расширение Markdown."""
        if extension not in self.extensions:
            self.extensions.append(extension)
            if config:
                self.extension_configs[extension] = config
            self._md = markdown.Markdown(
                extensions=self.extensions,
                extension_configs=self.extension_configs
            )

    def validate(self, content: str) -> bool:
        """Валидирует Markdown контент."""
        if not content.strip():
            return False
        return True

    def get_metadata(self, content: str) -> Dict[str, Any]:
        """Получает метаданные из Markdown контента."""
        try:
            post = frontmatter.loads(content)
            metadata = dict(post.metadata)
            
            # Преобразуем строковую дату в объект datetime
            if 'date' in metadata and isinstance(metadata['date'], str):
                try:
                    metadata['date'] = datetime.strptime(
                        metadata['date'], 
                        '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass
                    
            return metadata
        except Exception:
            return {}
