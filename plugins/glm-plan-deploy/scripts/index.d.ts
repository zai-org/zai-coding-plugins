#!/usr/bin/env node
/**
 * Deploy current folder as a nodejs project to cloud
 *
 * @param ignoreFilePath - Path to the .ignore file
 * @returns Promise containing deployment result with public URL and metadata
 *
 * @example
 * ```typescript
 * const result = await deploySkill('/path/to/.ignore');
 * if (result.success) {
 *   console.log('Deployed to:', result.url);
 *   console.log('Project metadata:', result.metadata);
 * } else {
 *   console.error('Deployment failed:', result.error);
 * }
 * ```
 */
export declare function deploySkill(ignoreFilePath: string): Promise<{
    success: true;
    url: string;
    message: string;
    metadata?: any;
} | {
    success: false;
    error: string;
}>;
export declare function statusSkill(): Promise<{
    success: true;
    status: string;
    message: string;
    metadata?: any;
} | {
    success: false;
    error: string;
}>;
export declare function zipSkill(targetPath: string, ignoreFilePath: string): Promise<{
    success: true;
    status: string;
    message: string;
    metadata?: any;
} | {
    success: false;
    error: string;
}>;
export declare function testSkill(): Promise<{
    success: true;
    message: string;
} | {
    success: false;
    error: string;
}>;
//# sourceMappingURL=index.d.ts.map