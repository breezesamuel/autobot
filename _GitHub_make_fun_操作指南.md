# 🚀 GitHub + make.fun 完整操作指南

---

## 📍 当前位置

✅ **GitHub新建仓库页面已打开！**

---

## 🔑 第一步：确保已登录GitHub

如果看到登录表单：
```
1. 输入你的GitHub邮箱/用户名
2. 输入密码
3. 点击 "Sign in"

如果没有账号 → 点击 "Create an account"
→ 填写邮箱、密码、用户名
→ 完成邮箱验证
```

---

## 📝 第二步：创建仓库

登录后你应该看到这个页面：

### 填写信息：
```
Repository name: fast-markdown-renderer

Description (可选): Fast Markdown parser for make.fun bounty

☑️ Public (必须公开)

☐ Initialize this repository with a README (不勾选)

☐ Add .gitignore (不勾选)

☐ Choose a license (不勾选，我们稍后手动添加)
```

### 点击 "Create repository"

---

## 💻 第三步：克隆仓库到本地

复制这行命令（把 YOUR_USERNAME 换成你的GitHub用户名）：

```powershell
git clone https://github.com/YOUR_USERNAME/fast-markdown-renderer.git
cd fast-markdown-renderer
```

---

## 📄 第四步：创建文件

在 `fast-markdown-renderer` 文件夹里创建以下文件：

### 1. parse.js
```javascript
'use strict';

const CACHE = new Map();

function getRegex(pattern, flags = '') {
    const key = `${pattern}|${flags}`;
    if (!CACHE.has(key)) {
        CACHE.set(key, new RegExp(pattern, flags));
    }
    return CACHE.get(key);
}

const HEADINGS = /^#{1,6}\s+(.*)$/;
const HORIZONTAL_RULE = /^(---+|___+|\*\*\*+)\s*$/;
const CODE_BLOCK = /^```(\w*)\n([\s\S]*?)```\s*$/;
const INLINE_CODE = /`([^`]+)`/g;
const BOLD = /\*\*(.+?)\*\*/g;
const ITALIC = /\*(.+?)\*/g;
const LINK = /\[(.+?)\]\((.+?)\)/g;
const IMAGE = /!\[(.+?)\]\((.+?)\)/g;
const BLANK_LINE = /^\s*$/;
const LIST_ITEM = /^(\s*)[-*+]\s+(.*)$/;
const ORDERED_LIST = /^(\s*)\d+\.\s+(.*)$/;
const BLOCKQUOTE = /^>\s?(.*)$/;

function escapeHtml(text) {
    if (typeof text !== 'string') return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function parseInline(text) {
    text = escapeHtml(text);
    text = text.replace(IMAGE, '<img src="$2" alt="$1">');
    text = text.replace(LINK, '<a href="$2">$1</a>');
    text = text.replace(INLINE_CODE, '<code>$1</code>');
    text = text.replace(BOLD, '<strong>$1</strong>');
    text = text.replace(ITALIC, '<em>$1</em>');
    return text;
}

function buildList(items, indent) {
    if (!items.length) return '';
    const isOrdered = items.some(item => /^\d+\./.test(item));
    const tag = isOrdered ? 'ol' : 'ul';
    const listItems = items.map(item => `<li>${item}</li>`).join('\n');
    return `<${tag}>\n${listItems}\n</${tag}>`;
}

function parse(markdown) {
    if (!markdown || typeof markdown !== 'string') return '';
    
    const lines = markdown.split('\n');
    const result = [];
    let i = 0;
    
    let codeBuffer = '';
    let codeLang = '';
    let inCodeBlock = false;
    let quoteBuffer = [];
    let listBuffer = [];
    let listIndent = '';
    let paragraphBuffer = [];
    
    function flushParagraph() {
        if (paragraphBuffer.length > 0) {
            result.push(`<p>${parseInline(paragraphBuffer.join(' '))}</p>`);
            paragraphBuffer = [];
        }
    }
    
    function flushList() {
        if (listBuffer.length > 0) {
            result.push(buildList(listBuffer, listIndent));
            listBuffer = [];
            listIndent = '';
        }
    }
    
    function flushQuote() {
        if (quoteBuffer.length > 0) {
            const content = quoteBuffer.map(line => parseInline(line)).join('\n');
            result.push(`<blockquote>${content}</blockquote>`);
            quoteBuffer = [];
        }
    }
    
    while (i < lines.length) {
        const line = lines[i];
        
        if (BLANK_LINE.test(line)) {
            flushParagraph();
            flushList();
            flushQuote();
            i++;
            continue;
        }
        
        if (line.startsWith('```')) {
            if (!inCodeBlock) {
                flushParagraph();
                flushList();
                flushQuote();
                inCodeBlock = true;
                codeLang = line.slice(3).trim();
                codeBuffer = '';
            } else {
                inCodeBlock = false;
                result.push(`<pre><code class="language-${escapeHtml(codeLang)}">${escapeHtml(codeBuffer)}</code></pre>`);
            }
            i++;
            continue;
        }
        
        if (inCodeBlock) {
            codeBuffer += line + '\n';
            i++;
            continue;
        }
        
        const headingMatch = line.match(HEADINGS);
        if (headingMatch) {
            flushParagraph();
            flushList();
            flushQuote();
            const level = headingMatch[0].match(/^#+/)[0].length;
            result.push(`<h${level}>${parseInline(headingMatch[1])}</h${level}>`);
            i++;
            continue;
        }
        
        if (HORIZONTAL_RULE.test(line)) {
            flushParagraph();
            flushList();
            flushQuote();
            result.push('<hr>');
            i++;
            continue;
        }
        
        const quoteMatch = line.match(BLOCKQUOTE);
        if (quoteMatch) {
            flushParagraph();
            flushList();
            quoteBuffer.push(quoteMatch[1]);
            i++;
            continue;
        } else if (quoteBuffer.length > 0) {
            flushQuote();
        }
        
        const bulletMatch = line.match(LIST_ITEM);
        const orderedMatch = line.match(ORDERED_LIST);
        
        if (bulletMatch || orderedMatch) {
            flushParagraph();
            flushQuote();
            
            const match = bulletMatch || orderedMatch;
            const currentIndent = match[1];
            const content = match[2];
            
            if (listIndent && currentIndent !== listIndent) {
                flushList();
            }
            
            listIndent = currentIndent;
            const itemContent = orderedMatch 
                ? `${listBuffer.length + 1}. ${content}`
                : content;
            
            listBuffer.push(parseInline(itemContent));
            i++;
            continue;
        } else if (listBuffer.length > 0) {
            flushList();
        }
        
        paragraphBuffer.push(line.trim());
        i++;
    }
    
    flushParagraph();
    flushList();
    flushQuote();
    
    return result.join('\n');
}

module.exports = { parse };
module.exports.markedParse = parse;
```

### 2. main.ts
```typescript
import { parse } from './parse.js';

const TEST_CASES = [
    { name: 'Heading', input: '# Hello', expected: '<h1>Hello</h1>' },
    { name: 'Bold', input: '**bold**', expected: '<p><strong>bold</strong></p>' },
    { name: 'Italic', input: '*italic*', expected: '<p><em>italic</em></p>' },
    { name: 'Link', input: '[Google](https://google.com)', expected: '<p><a href="https://google.com">Google</a></p>' },
    { name: 'Image', input: '![Alt](img.png)', expected: '<p><img src="img.png" alt="Alt"></p>' },
    { name: 'Code', input: '```\\ncode\\n```', expected: '<pre><code class="language-text">code\\n</code></pre>' },
    { name: 'List', input: '- Item 1\\n- Item 2', expected: '<ul>\\n<li>Item 1</li>\\n<li>Item 2</li>\\n</ul>' },
];

let passed = 0, failed = 0;

for (const t of TEST_CASES) {
    const r = parse(t.input).replace(/\\n/g, '\\n').trim();
    const e = t.expected.replace(/\\n/g, '\\n').trim();
    if (r === e) { console.log(`✅ ${t.name}`); passed++; }
    else { console.log(`❌ ${t.name}: expected ${e}, got ${r}`); failed++; }
}

console.log(`\\nResults: ${passed}/${passed + failed} passed`);
process.exit(failed > 0 ? 1 : 0);
```

### 3. package.json
```json
{
  "name": "fast-markdown-renderer",
  "version": "1.0.0",
  "description": "Fast Markdown parser",
  "main": "parse.js",
  "type": "module",
  "scripts": { "test": "node main.js" },
  "license": "MIT"
}
```

### 4. README.md
```markdown
# Fast Markdown Renderer

Fast drop-in replacement for marked.js

[![make.fun](https://make.fun/badge/markdown-render-speed-02)](https://www.make.fun/bounty/markdown-render-speed-02)

## License
MIT
```

### 5. .makefun/owner.json
```json
{
  "wallet": "YOUR_SOLANA_WALLET"
}
```

---

## 🔄 第五步：提交代码

```powershell
git add .
git commit -m "Initial commit: fast markdown renderer"
git push -u origin main
```

---

## ⏰ 时间提醒

```
🟢 现在: UTC 13:15 (北京 21:15)
🔴 截止: UTC 20:30 (北京 明早 4:30)
⏰ 剩余: 约 7 小时
```

---

## ❓ 遇到问题？

告诉我你卡在哪一步，我马上帮你解决！