export declare class FileFilter {
    private ignoreRules;
    private basePath;
    constructor(basePath: string);
    /**
     * 从 .ignore 文件加载规则
     */
    loadIgnoreFile(ignoreFilePath?: string): Promise<void>;
    /**
     * 解析 ignore 规则
     */
    private parseIgnoreRules;
    /**
     * 将通配符模式转换为正则表达式
     */
    private patternToRegex;
    /**
     * 检查文件路径是否被忽略
     */
    private isIgnored;
    /**
     * 简单的模式匹配（作为正则表达式的后备）
     */
    private simplePatternMatch;
    /**
     * 递归扫描目录并过滤文件
     */
    filterDirectory(dirPath?: string): Promise<string[]>;
    /**
     * 获取过滤后的所有文件列表（相对路径）
     */
    getFilteredFiles(): Promise<string[]>;
    /**
     * 手动添加 ignore 规则
     */
    addRule(pattern: string, isNegated?: boolean): void;
    /**
     * 清除所有规则
     */
    clearRules(): void;
}
/**
 * 便捷函数：根据 .ignore 文件过滤目录文件
 * @param directoryPath 要过滤的目录路径
 * @param ignoreFile ignore 文件路径（默认为 '.ignore'）
 * @returns 过滤后的文件相对路径列表
 */
export declare function filterDirectoryFiles(directoryPath: string, ignoreFile?: string): Promise<string[]>;
//# sourceMappingURL=filterFiles.d.ts.map