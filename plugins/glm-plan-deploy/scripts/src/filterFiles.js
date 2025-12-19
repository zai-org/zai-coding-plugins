"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.FileFilter = void 0;
exports.filterDirectoryFiles = filterDirectoryFiles;
const fs = __importStar(require("fs/promises"));
const path = __importStar(require("path"));
class FileFilter {
    ignoreRules = [];
    basePath;
    constructor(basePath) {
        this.basePath = path.resolve(basePath);
    }
    /**
     * 从 .ignore 文件加载规则
     */
    async loadIgnoreFile(ignoreFilePath = '.ignore') {
        try {
            const content = await fs.readFile(ignoreFilePath, 'utf-8');
            this.parseIgnoreRules(content);
        }
        catch (error) {
            console.warn(`Warning: Could not read ignore file at ${ignoreFilePath}: ${error}`);
        }
    }
    /**
     * 解析 ignore 规则
     */
    parseIgnoreRules(content) {
        const lines = content.split('\n');
        for (const line of lines) {
            const trimmedLine = line.trim();
            // 跳过空行和注释
            if (!trimmedLine || trimmedLine.startsWith('#')) {
                continue;
            }
            // 解析规则
            const isNegated = trimmedLine.startsWith('!');
            const pattern = isNegated ? trimmedLine.slice(1) : trimmedLine;
            const isDirectory = pattern.endsWith('/');
            const cleanPattern = isDirectory ? pattern.slice(0, -1) : pattern;
            this.ignoreRules.push({
                pattern: cleanPattern,
                isNegated,
                isDirectory,
                regex: this.patternToRegex(cleanPattern)
            });
        }
    }
    /**
     * 将通配符模式转换为正则表达式
     */
    patternToRegex(pattern) {
        // 转义正则表达式特殊字符，但保留通配符
        let regexPattern = pattern
            .replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
            .replace(/\\\*/g, '.*')
            .replace(/\\\?/g, '.');
        // 处理路径开始和结束的锚点
        if (!pattern.includes('/')) {
            // 如果模式不包含斜杠，可以匹配任何位置的文件名
            regexPattern = `(?:^|/)${regexPattern}(?:$|/)`;
        }
        else if (!pattern.startsWith('/')) {
            // 如果模式不以斜杠开头，可以匹配任何子路径
            regexPattern = `(?:^|.*/)${regexPattern}`;
        }
        else {
            // 如果模式以斜杠开头，只匹配根路径
            regexPattern = `^${regexPattern.slice(1)}`;
        }
        return new RegExp(regexPattern);
    }
    /**
     * 检查文件路径是否被忽略
     */
    isIgnored(relativePath, isDirectory) {
        let isIgnored = false;
        for (const rule of this.ignoreRules) {
            // 检查目录匹配规则
            if (rule.isDirectory && !isDirectory) {
                continue;
            }
            // 使用正则表达式匹配
            if (rule.regex && rule.regex.test(relativePath)) {
                isIgnored = !rule.isNegated;
            }
            // 或者进行简单的字符串匹配（作为后备）
            else if (this.simplePatternMatch(rule.pattern, relativePath)) {
                isIgnored = !rule.isNegated;
            }
        }
        return isIgnored;
    }
    /**
     * 简单的模式匹配（作为正则表达式的后备）
     */
    simplePatternMatch(pattern, path) {
        if (pattern === path)
            return true;
        if (pattern.endsWith('/')) {
            return path.startsWith(pattern) || path === pattern.slice(0, -1);
        }
        if (pattern.includes('*')) {
            const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
            return regex.test(path);
        }
        return path.includes(pattern);
    }
    /**
     * 递归扫描目录并过滤文件
     */
    async filterDirectory(dirPath = this.basePath) {
        const results = [];
        const relativeDirPath = path.relative(this.basePath, dirPath);
        // 检查当前目录是否被忽略
        if (relativeDirPath && this.isIgnored(relativeDirPath, true)) {
            console.info(`Ignoring directory: ${relativeDirPath}/`);
            return results;
        }
        try {
            const entries = await fs.readdir(dirPath, { withFileTypes: true });
            for (const entry of entries) {
                const fullPath = path.join(dirPath, entry.name);
                const relativePath = path.relative(this.basePath, fullPath);
                // 检查是否被忽略
                if (this.isIgnored(relativePath, entry.isDirectory())) {
                    console.info(`Ignoring ${entry.isDirectory() ? 'directory' : 'file'}: ${relativePath}`);
                    continue;
                }
                if (entry.isDirectory()) {
                    // 递归处理子目录
                    const subResults = await this.filterDirectory(fullPath);
                    results.push(...subResults);
                }
                else {
                    // 添加文件路径
                    results.push(relativePath);
                }
            }
        }
        catch (error) {
            console.warn(`Warning: Could not read directory ${dirPath}: ${error}`);
        }
        return results;
    }
    /**
     * 获取过滤后的所有文件列表（相对路径）
     */
    async getFilteredFiles() {
        return await this.filterDirectory();
    }
    /**
     * 手动添加 ignore 规则
     */
    addRule(pattern, isNegated = false) {
        const isDirectory = pattern.endsWith('/');
        const cleanPattern = isDirectory ? pattern.slice(0, -1) : pattern;
        this.ignoreRules.push({
            pattern: cleanPattern,
            isNegated,
            isDirectory,
            regex: this.patternToRegex(cleanPattern)
        });
    }
    /**
     * 清除所有规则
     */
    clearRules() {
        this.ignoreRules = [];
    }
}
exports.FileFilter = FileFilter;
/**
 * 便捷函数：根据 .ignore 文件过滤目录文件
 * @param directoryPath 要过滤的目录路径
 * @param ignoreFile ignore 文件路径（默认为 '.ignore'）
 * @returns 过滤后的文件相对路径列表
 */
async function filterDirectoryFiles(directoryPath, ignoreFile = '.ignore') {
    const filter = new FileFilter(directoryPath);
    await filter.loadIgnoreFile(ignoreFile);
    return await filter.getFilteredFiles();
}
//# sourceMappingURL=filterFiles.js.map