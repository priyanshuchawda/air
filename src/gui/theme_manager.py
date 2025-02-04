class ThemeManager:
    THEMES = {
        'dark': {
            'background': '#2D2D2D',
            'text': '#FFFFFF',
            'button': '#3E3E3E',
            'highlight': '#2196F3'
        },
        'light': {
            'background': '#FFFFFF',
            'text': '#000000',
            'button': '#F0F0F0',
            'highlight': '#2196F3'
        },
        'high_contrast': {
            'background': '#000000',
            'text': '#FFFF00',
            'button': '#FFFFFF',
            'highlight': '#FF0000'
        }
    }

    def apply_theme(self, theme_name, app):
        theme = self.THEMES.get(theme_name, self.THEMES['dark'])
        style = f"""
            QWidget {{
                background-color: {theme['background']};
                color: {theme['text']};
            }}
            QPushButton {{
                background-color: {theme['button']};
                border: 2px solid {theme['highlight']};
                padding: 8px;
                border-radius: 4px;
            }}
        """
        app.setStyleSheet(style)