"""Utilities for generating Pygments CSS styles."""
from pygments.formatters import HtmlFormatter
import logging

logger = logging.getLogger(__name__)

# Список доступных стилей для документации
AVAILABLE_STYLES = [
    "monokai", "default", "emacs", "vs", "xcode", "colorful", 
    "dracula", "github", "gruvbox-dark", "solarized-dark", "solarized-light",
    "nord", "tango", "zenburn"
]

def generate_pygments_css(style_name="monokai", custom_styles=None):
    """
    Generate Pygments CSS for syntax highlighting.
    
    Args:
        style_name: The Pygments style name to use (default: monokai)
        custom_styles: Additional CSS styles to append to the generated CSS
        
    Returns:
        str: Complete CSS for syntax highlighting
    """
    try:
        # Получаем базовые стили от Pygments для выбранной темы
        formatter = HtmlFormatter(style=style_name)
        pygments_css = formatter.get_style_defs('.highlight')
        
        # Добавляем минимальные необходимые стили для корректного отображения
        essential_css = """
/* Основные стили для корректного отображения */
.highlight {
    tab-size: 4 !important;
    -moz-tab-size: 4 !important;
    -o-tab-size: 4 !important;
    -webkit-tab-size: 4 !important;
    white-space: pre !important;
    letter-spacing: normal !important;
    word-spacing: normal !important;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.highlight pre {
    padding: 1em;
    margin: 0;
    overflow-x: auto;
    background: transparent !important;
    white-space: pre !important;
    display: block !important;
}

.highlight code {
    display: block !important;
    background: transparent;
    color: inherit;
    white-space: pre !important;
    position: relative;
}

/* Стили для строк */
.highlight .line {
    display: block !important;
    white-space: pre !important;
    position: relative;
    padding-left: 0;
    min-height: 1.2em;
}

/* Стили для пробелов */
.highlight .w {
    display: inline-block !important;
    white-space: pre !important;
    color: inherit !important;
    width: 0.6em !important;
    min-width: 0.6em !important;
    visibility: visible !important;
}

/* Специальные классы для отступов в начале строки */
.highlight .ws {
    white-space: pre !important;
    display: inline-block !important;
    visibility: visible !important;
    color: transparent !important;
    position: relative !important;
    width: 0.6em !important;
    min-width: 0.6em !important;
}

/* Стили для span элементов внутри highlight */
.highlight span {
    white-space: pre !important;
    display: inline-block !important;
}

/* Фиксированная ширина для пробелов после ключевых слов */
.highlight .k + .w,
.highlight .kd + .w,
.highlight .kr + .w,
.highlight .kt + .w {
    width: 0.6em !important;
    min-width: 0.6em !important;
    display: inline-block !important;
    visibility: visible !important;
}

/* Принудительные переносы строк */
.highlight br {
    display: block !important;
    content: "" !important;
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    line-height: inherit !important;
}

/* Стили для кода с табуляцией */
.highlight.has-tabs {
    position: relative;
}

/* Стили для блока кода */
.code-block {
    position: relative;
    margin: 1em 0;
    border-radius: 4px;
    overflow: hidden;
    background: #272822;
    color: #f8f8f2;
}

.language-tag {
    position: absolute;
    top: 0;
    right: 0;
    padding: 2px 8px;
    background: #333;
    color: #fff;
    font-size: 12px;
    border-radius: 0 0 0 4px;
    z-index: 10;
}

/* Специфичные стили для разных языков */
.language-python .k + .n,
.language-javascript .k + .n,
.language-typescript .k + .n,
.language-java .k + .n,
.language-csharp .k + .n,
.language-go .k + .n,
.language-rust .k + .n,
.language-swift .k + .n,
.language-kotlin .k + .n {
    margin-left: 0.25em !important;
}

/* Стили для операторов */
.highlight .o, .highlight .ow {
    margin: 0 0.25em !important;
}

/* Стили для пунктуации */
.highlight .p {
    white-space: pre !important;
}

/* Фикс для отображения шаблонных строк JavaScript */
.highlight .sb, .highlight .s, .highlight .sa, .highlight .sc, 
.highlight .dl, .highlight .sd, .highlight .s2, .highlight .se, 
.highlight .sh, .highlight .si, .highlight .sx, .highlight .sr, 
.highlight .s1, .highlight .ss {
    white-space: pre !important;
}

/* Фикс для специальных символов во всех языках */
.highlight .nb, .highlight .nf, .highlight .nx, .highlight .nc {
    margin-left: 0.25em !important;
}

/* JavaScript специфичные фиксы */
.language-javascript .sb code.inline-code,
.javascript .sb code.inline-code,
.language-js .sb code.inline-code,
.js .sb code.inline-code {
    background: transparent !important;
    padding: 0 !important;
    font-family: inherit !important;
    font-size: inherit !important;
    display: inline !important;
}

/* Ruby специфичные фиксы */
.language-ruby .n, .ruby .n {
    margin-left: 0.25em !important;
}

/* PHP специфичные фиксы */
.language-php .k + .n, .php .k + .n {
    margin-left: 0.25em !important;
}

/* C/C++ специфичные фиксы */
.language-c .kt + .n, .language-cpp .kt + .n, 
.c .kt + .n, .cpp .kt + .n {
    margin-left: 0.25em !important;
}

/* Java специфичные фиксы */
.language-java .kd + .n, .java .kd + .n {
    margin-left: 0.25em !important;
}

/* C# специфичные фиксы */
.language-csharp .k + .n, .csharp .k + .n {
    margin-left: 0.25em !important;
}

/* Go специфичные фиксы */
.language-go .k + .n, .go .k + .n {
    margin-left: 0.25em !important;
}

/* Rust специфичные фиксы */
.language-rust .k + .n, .rust .k + .n {
    margin-left: 0.25em !important;
}

/* TypeScript специфичные фиксы */
.language-typescript .k + .n, .typescript .k + .n,
.language-ts .k + .n, .ts .k + .n {
    margin-left: 0.25em !important;
}

/* Swift специфичные фиксы */
.language-swift .k + .n, .swift .k + .n {
    margin-left: 0.25em !important;
}

/* Kotlin специфичные фиксы */
.language-kotlin .k + .n, .kotlin .k + .n {
    margin-left: 0.25em !important;
}

"""
        css = f"{pygments_css}\n\n{essential_css}"
        if custom_styles:
            css = f"{css}\n\n{custom_styles}"
        return css
    except Exception as e:
        logger.error(f"Error generating Pygments CSS: {e}")
        return "/* Error generating Pygments CSS */"
