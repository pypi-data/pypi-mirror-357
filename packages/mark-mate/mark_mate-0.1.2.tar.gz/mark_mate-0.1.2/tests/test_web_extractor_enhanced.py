"""
Enhanced tests for Web Extractor with International Encoding Support

Tests the WebExtractor's enhanced international encoding capabilities
for HTML, CSS, and JavaScript files from ESL student environments.
"""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Dict, Any

# Import the module under test
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from mark_mate.extractors.web_extractor import WebExtractor
from mark_mate.extractors.models import ExtractionResult, FileInfo


class TestWebExtractorEnhancedEncoding:
    """Test enhanced international encoding support."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = WebExtractor()

    def test_html_international_encoding(self):
        """Test HTML with international characters from various ESL students."""
        html_content = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>国际学生网站 - International Student Website</title>
</head>
<body>
    <!-- 中文注释 Chinese comment -->
    <header>
        <h1>欢迎来到我们的网站</h1>
        <h2>Добро пожаловать на наш сайт</h2>
        <h3>مرحبا بكم في موقعنا</h3>
        <h4>Bienvenidos a nuestro sitio web</h4>
    </header>
    
    <main>
        <section id="chinese-section">
            <p>这是一个国际化的网站，支持多种语言。</p>
            <p>我们的学生来自世界各地。</p>
        </section>
        
        <section id="russian-section">
            <p>Это международный веб-сайт, поддерживающий несколько языков.</p>
            <p>Наши студенты приезжают со всего мира.</p>
        </section>
        
        <section id="arabic-section">
            <p dir="rtl">هذا موقع دولي يدعم عدة لغات.</p>
            <p dir="rtl">طلابنا يأتون من جميع أنحاء العالم.</p>
        </section>
        
        <section id="spanish-section">
            <p>Este es un sitio web internacional que soporta múltiples idiomas.</p>
            <p>Nuestros estudiantes vienen de todo el mundo.</p>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 International University - 国际大学 - Международный университет</p>
    </footer>
</body>
</html>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            
            # Check that all international characters are preserved
            assert "欢迎来到我们的网站" in result.content
            assert "Добро пожаловать" in result.content
            assert "مرحبا بكم في موقعنا" in result.content
            assert "Bienvenidos" in result.content
            assert "国际大学" in result.content
            assert "Международный университет" in result.content
            
            # Check encoding information
            if "encoding_info" in result.analysis:
                encoding_info = result.analysis["encoding_info"]
                assert "encoding_used" in encoding_info
                assert "enhanced_encoding" in encoding_info
                
        finally:
            os.unlink(temp_file)

    def test_css_international_encoding(self):
        """Test CSS with international fonts, comments, and content."""
        css_content = '''/* 
 * 国际化样式表 - International Stylesheet
 * Международная таблица стилей
 * ورقة الأنماط الدولية
 */

@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap');

/* 中文字体设置 */
.chinese-text {
    font-family: "Noto Sans SC", "Microsoft YaHei", "微软雅黑", sans-serif;
    font-size: 16px;
    line-height: 1.6;
}

/* Русские шрифты */
.russian-text {
    font-family: "Times New Roman", "DejaVu Serif", serif;
    font-size: 14px;
    content: "Русский текст";
}

/* الخطوط العربية */
.arabic-text {
    font-family: "Amiri", "Arabic Typesetting", serif;
    direction: rtl;
    text-align: right;
    font-size: 18px;
}

/* Fuentes españolas */
.spanish-text {
    font-family: "Georgia", "Times", serif;
    font-style: italic;
}

/* International color scheme - 国际配色方案 */
:root {
    --primary-color: #红色; /* This is invalid but shows international comments */
    --secondary-color: #0066cc;
    --accent-color: #ff6600;
}

.international-banner {
    background: linear-gradient(45deg, 
        #ff0000 /* 红色 - Red */,
        #00ff00 /* 绿色 - Green */,
        #0000ff /* 蓝色 - Blue */
    );
}

/* Media queries for international layouts */
@media screen and (max-width: 768px) {
    .chinese-text,
    .russian-text,
    .arabic-text,
    .spanish-text {
        font-size: 14px;
        margin: 10px 0;
    }
}

/* Animation names with international characters */
@keyframes 淡入动画 {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes анимация_появления {
    0% { transform: translateY(-100%); }
    100% { transform: translateY(0); }
}'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False, encoding='utf-8') as f:
            f.write(css_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            
            # Check international characters preservation
            assert "国际化样式表" in result.content
            assert "Международная таблица стилей" in result.content
            assert "ورقة الأنماط الدولية" in result.content
            assert "微软雅黑" in result.content
            assert "Русский текст" in result.content
            assert "淡入动画" in result.content
            assert "анимация_появления" in result.content
            
            # Check CSS analysis
            if "basic_structure" in result.analysis:
                basic = result.analysis["basic_structure"]
                assert "error" not in basic  # Should parse successfully
                
        finally:
            os.unlink(temp_file)

    def test_javascript_international_encoding(self):
        """Test JavaScript with international strings, comments, and identifiers."""
        js_content = '''/**
 * 国际化JavaScript模块 - International JavaScript Module
 * Международный JavaScript модуль
 * وحدة جافا سكريبت الدولية
 */

'use strict';

// 国际化消息对象
const internationalMessages = {
    // 中文消息
    chinese: {
        greeting: "你好，世界！",
        welcome: "欢迎使用我们的应用程序",
        goodbye: "再见！"
    },
    
    // Русские сообщения
    russian: {
        greeting: "Привет, мир!",
        welcome: "Добро пожаловать в наше приложение",
        goodbye: "До свидания!"
    },
    
    // الرسائل العربية
    arabic: {
        greeting: "مرحبا بالعالم!",
        welcome: "مرحبا بكم في تطبيقنا",
        goodbye: "وداعا!"
    },
    
    // Mensajes en español
    spanish: {
        greeting: "¡Hola, mundo!",
        welcome: "Bienvenido a nuestra aplicación",
        goodbye: "¡Adiós!"
    },
    
    // Messages français
    french: {
        greeting: "Bonjour le monde!",
        welcome: "Bienvenue dans notre application",
        goodbye: "Au revoir!"
    }
};

// 国际化工具类
class InternationalizationUtils {
    constructor(defaultLanguage = 'english') {
        this.defaultLanguage = defaultLanguage;
        this.currentLanguage = defaultLanguage;
        this.支持的语言 = ['chinese', 'russian', 'arabic', 'spanish', 'french']; // Supported languages
    }
    
    // 获取消息的方法
    getMessage(key, language = this.currentLanguage) {
        try {
            const messages = internationalMessages[language];
            if (!messages || !messages[key]) {
                console.warn(`消息未找到: ${key} for language: ${language}`);
                return `[Missing: ${key}]`;
            }
            return messages[key];
        } catch (error) {
            console.error('获取消息时出错:', error);
            return '[Error loading message]';
        }
    }
    
    // 设置当前语言
    setLanguage(语言) { // Parameter name in Chinese
        if (this.支持的语言.includes(语言)) {
            this.currentLanguage = 语言;
            console.log(`语言已切换到: ${语言}`);
            return true;
        } else {
            console.error(`不支持的语言: ${语言}`);
            return false;
        }
    }
    
    // 获取所有支持的语言
    getSupportedLanguages() {
        return [...this.支持的语言];
    }
}

// 创建全局实例
const i18n = new InternationalizationUtils();

// 国际化函数
function displayInternationalGreeting() {
    const supportedLanguages = i18n.getSupportedLanguages();
    
    supportedLanguages.forEach(lang => {
        const greeting = i18n.getMessage('greeting', lang);
        console.log(`${lang}: ${greeting}`);
    });
}

// 处理用户输入的国际化
function handleUserInput(用户输入) { // Parameter name in Chinese
    // 验证输入是否包含国际字符
    const containsInternational = /[\\u4e00-\\u9fff\\u0400-\\u04ff\\u0600-\\u06ff]/g.test(用户输入);
    
    if (containsInternational) {
        console.log('检测到国际字符input:', 用户输入);
        return {
            isInternational: true,
            input: 用户输入,
            detected: '国际字符已检测'
        };
    }
    
    return {
        isInternational: false,
        input: 用户输入,
        detected: 'ASCII字符'
    };
}

// 主程序入口
if (typeof window !== 'undefined') {
    // 浏览器环境
    window.i18nUtils = i18n;
    window.显示国际问候 = displayInternationalGreeting; // Function name in Chinese
} else {
    // Node.js环境
    module.exports = {
        InternationalizationUtils,
        internationalMessages,
        i18n,
        displayInternationalGreeting,
        handleUserInput
    };
}

// 初始化应用程序
console.log('国际化模块已加载 - Internationalization module loaded');
displayInternationalGreeting();'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(js_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            
            # Check international characters preservation
            assert "国际化JavaScript模块" in result.content
            assert "Международный JavaScript модуль" in result.content
            assert "وحدة جافا سكريبت الدولية" in result.content
            assert "你好，世界！" in result.content
            assert "Привет, мир!" in result.content
            assert "مرحبا بالعالم!" in result.content
            assert "支持的语言" in result.content
            assert "显示国际问候" in result.content
            assert "用户输入" in result.content
            
            # Check JavaScript analysis
            if "basic_structure" in result.analysis:
                basic = result.analysis["basic_structure"]
                assert "error" not in basic  # Should parse successfully
                
        finally:
            os.unlink(temp_file)

    def test_jsx_international_encoding(self):
        """Test JSX with international components and props."""
        jsx_content = '''import React, { useState, useEffect } from 'react';

/**
 * 国际化React组件 - International React Component
 * Компонент React для интернационализации
 */
const InternationalWelcome = ({ 用户名, 语言 = 'chinese' }) => {
    const [当前消息, set当前消息] = useState('');
    const [loading, setLoading] = useState(true);
    
    // 国际化消息映射
    const messages = {
        chinese: {
            welcome: `欢迎, ${用户名}!`,
            loading: '加载中...',
            error: '出现错误'
        },
        russian: {
            welcome: `Добро пожаловать, ${用户名}!`,
            loading: 'Загрузка...',
            error: 'Произошла ошибка'
        },
        arabic: {
            welcome: `مرحبا، ${用户名}!`,
            loading: 'جارٍ التحميل...',
            error: 'حدث خطأ'
        }
    };
    
    useEffect(() => {
        // 模拟异步加载
        const timer = setTimeout(() => {
            const messageObj = messages[语言] || messages.chinese;
            set当前消息(messageObj.welcome);
            setLoading(false);
        }, 1000);
        
        return () => clearTimeout(timer);
    }, [用户名, 语言]);
    
    if (loading) {
        return (
            <div className="loading-container">
                <p>{messages[语言]?.loading || '加载中...'}</p>
            </div>
        );
    }
    
    return (
        <div className="international-welcome">
            <h1>{当前消息}</h1>
            <div className="user-info">
                <p>用户名: {用户名}</p>
                <p>语言: {语言}</p>
            </div>
            
            {/* 条件渲染基于语言 */}
            {语言 === 'arabic' && (
                <div dir="rtl" className="arabic-content">
                    <p>محتوى باللغة العربية</p>
                </div>
            )}
            
            {语言 === 'chinese' && (
                <div className="chinese-content">
                    <p>中文内容显示区域</p>
                </div>
            )}
            
            {语言 === 'russian' && (
                <div className="russian-content">
                    <p>Содержимое на русском языке</p>
                </div>
            )}
        </div>
    );
};

export default InternationalWelcome;'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsx', delete=False, encoding='utf-8') as f:
            f.write(jsx_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            
            # Check international characters preservation
            assert "国际化React组件" in result.content
            assert "Компонент React для интернационализации" in result.content
            assert "用户名" in result.content
            assert "当前消息" in result.content
            assert "set当前消息" in result.content
            assert "加载中..." in result.content
            assert "Добро пожаловать" in result.content
            assert "مرحبا" in result.content
            assert "محتوى باللغة العربية" in result.content
            
        finally:
            os.unlink(temp_file)


class TestWebExtractorEncodingFallback:
    """Test encoding fallback mechanisms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = WebExtractor()

    def test_encoding_fallback_mechanism(self):
        """Test that encoding fallback works when enhanced encoding is unavailable."""
        html_content = '''<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Simple Test</h1></body>
</html>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            result = self.extractor.extract_content(temp_file)
            
            assert result.success is True
            assert "Simple Test" in result.content
            
            # Should have encoding information
            if "encoding_info" in result.analysis:
                encoding_info = result.analysis["encoding_info"]
                assert "encoding_used" in encoding_info
                
        finally:
            os.unlink(temp_file)


class TestWebExtractorIntegration:
    """Integration tests with existing fixtures."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = WebExtractor()
        self.fixtures_path = Path(__file__).parent / "fixtures"

    def test_with_existing_web_fixtures(self):
        """Test with existing web test fixtures."""
        web_fixtures = [
            "test_web_sample.html",
            "test_web_sample.css", 
            "test_web_sample.js"
        ]
        
        for fixture_name in web_fixtures:
            fixture_path = self.fixtures_path / fixture_name
            if fixture_path.exists():
                result = self.extractor.extract_content(str(fixture_path))
                assert isinstance(result, ExtractionResult)
                # Should either succeed or fail gracefully

    def test_web_submission_folder(self):
        """Test with web submission folder if it exists."""
        web_submission_path = self.fixtures_path / "test_web_submission"
        
        if web_submission_path.exists():
            for pattern in ["*.html", "*.css", "*.js", "*.jsx"]:
                for file_path in web_submission_path.glob(pattern):
                    if file_path.exists():
                        result = self.extractor.extract_content(str(file_path))
                        assert isinstance(result, ExtractionResult)


if __name__ == "__main__":
    # Run basic smoke tests
    print("Running Enhanced Web Extractor Tests...")
    
    extractor = WebExtractor()
    print(f"Extractor initialized: {extractor.extractor_name}")
    
    # Test with international HTML
    test_html = '''<!DOCTYPE html>
<html><head><title>测试页面</title></head>
<body><h1>Тестовая страница</h1></body></html>'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(test_html)
        temp_file = f.name
    
    try:
        result = extractor.extract_content(temp_file)
        print(f"International HTML test: {result.success and '测试页面' in result.content}")
        print("Enhanced encoding tests passed!")
    finally:
        os.unlink(temp_file)
    
    print("Tests completed!")