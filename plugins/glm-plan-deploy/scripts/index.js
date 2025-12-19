#!/usr/bin/env node
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deploySkill = deploySkill;
exports.statusSkill = statusSkill;
exports.zipSkill = zipSkill;
exports.testSkill = testSkill;
const path_1 = require("path");
const process_1 = require("process");
const utils_1 = require("./src/utils");
const filterFiles_1 = require("./src/filterFiles");
const fs_1 = require("fs");
const programDir = (0, path_1.dirname)(process.argv[1]);
(0, process_1.loadEnvFile)(`${programDir}/.env`);
const service_1 = require("./src/service");
// Show package version on module import
const packageJson = (0, utils_1.getPackageVersion)();
if (!packageJson || !packageJson.version) {
    console.error('Error: package.json not found or missing version');
    process.exit(1);
}
/**
 * Error handling wrapper for consistent error responses
 */
function handleUncaughtError(error) {
    const errorMessage = error?.message || 'Unknown error occurred';
    return {
        success: false,
        error: errorMessage
    };
}
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
async function deploySkill(ignoreFilePath) {
    try {
        // 1. find or create .deploy/settings.json, if package.json is not found, return error
        const { deploySettings, env } = await (0, utils_1.loadDeploySettings)();
        console.info('Deploy settings:', deploySettings);
        console.info('Environment variables:', env);
        // 2. zip folder
        const localFolder = process.cwd();
        const files = await (0, filterFiles_1.filterDirectoryFiles)(localFolder, ignoreFilePath);
        console.info(`filtered files count: ${files.length}`);
        // zip the files
        const tmpDir = (0, path_1.join)(localFolder, '.tmp');
        if (!(0, fs_1.existsSync)(tmpDir)) {
            (0, fs_1.mkdirSync)(tmpDir, { recursive: true });
        }
        // Create temporary zip file path
        const tmpZipFn = (0, path_1.join)(tmpDir, `${Date.now()}_upload.zip`);
        const file = await (0, utils_1.zipFiles)(tmpZipFn, files);
        // 3. upload and deploy
        let projectId = null;
        let deploymentId = null;
        try {
            console.info('Start to upload and deploy');
            const deploymentResult = await (0, service_1.uploadAndDeploy)(file, env, deploySettings.projectId);
            projectId = deploymentResult.projectId;
            deploymentId = deploymentResult.deploymentId;
            console.info(`Upload and deploy completed: projectId=${projectId}, deploymentId=${deploymentId}`);
        }
        finally {
            (0, fs_1.rmSync)(tmpZipFn);
        }
        if (projectId !== deploySettings.projectId) {
            deploySettings.projectId = projectId;
        }
        deploySettings.deployments = deploySettings.deployments || [];
        deploySettings.deployments.unshift({
            deploymentId: deploymentId,
            date: new Date().toISOString()
        });
        // save deploy settings
        await (0, utils_1.updateDeploySettings)(deploySettings);
        // 4. loop to get deployment result
        let status = { status: 'Pending', id: deploymentId };
        while (true) {
            status = await (0, service_1.getDeployStatus)(deploySettings.projectId, deploymentId);
            if (!(['Process', 'Pending'].includes(status.status))) {
                break;
            }
            console.info(`Deployment status: ${status.status}, waiting...`);
            await new Promise(resolve => setTimeout(resolve, 5000));
        }
        if (status.status === 'Success') {
            return {
                success: true,
                url: status.result?.previewUrl || '',
                message: 'Project deployed successfully',
                metadata: {
                    projectId,
                    deploymentId,
                    previewUrl: status.result?.previewUrl,
                    coverUrl: status.result?.coverUrl
                }
            };
        }
        else {
            return {
                success: false,
                error: `Deployment failed with status: ${status.status}, msg: ${status.result?.message || ''}`
            };
        }
    }
    catch (error) {
        return handleUncaughtError(error);
    }
}
async function statusSkill() {
    try {
        // 1. find or create .deploy/settings.json, if package.json is not found, return error
        const { deploySettings, } = await (0, utils_1.loadDeploySettings)();
        deploySettings.projectId;
        if (!deploySettings.projectId || deploySettings.deployments && deploySettings.deployments.length === 0) {
            return {
                success: false,
                error: 'Project ID not found in deploy settings. Please deploy first.'
            };
        }
        const status = await (0, service_1.getDeployStatus)(deploySettings.projectId, deploySettings.deployments[0].deploymentId);
        return {
            success: true,
            status: status.status,
            message: 'get status deployed successfully'
        };
    }
    catch (error) {
        return handleUncaughtError(error);
    }
}
async function zipSkill(targetPath, ignoreFilePath) {
    try {
        const zip = await (0, utils_1.zipFiles)(targetPath, await (0, filterFiles_1.filterDirectoryFiles)(process.cwd(), ignoreFilePath));
        return {
            success: true,
            status: 'zipped size:' + zip.size,
            message: 'zip executed successfully',
            metadata: {
                zipFile: zip
            }
        };
    }
    catch (error) {
        return handleUncaughtError(error);
    }
}
async function testSkill() {
    try {
        const folderList = await (0, filterFiles_1.filterDirectoryFiles)(process.cwd());
        console.info('Filtered files:', folderList);
        return {
            success: true,
            message: 'Test skill executed successfully'
        };
    }
    catch (error) {
        return handleUncaughtError(error);
    }
}
;
/**
 * CLI interface for direct command line usage
 */
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    const ignoreFilePath = `${programDir}/.ignore`;
    if (!command) {
        console.log(`
Usage:
  node index.ts deploy
  node index.ts status
    `);
        return;
    }
    switch (command) {
        case 'deploy': {
            const result = await deploySkill(ignoreFilePath);
            if (result.success) {
                console.log('✅ Deploy successful!');
                console.log('📍 URL:', result.url);
            }
            else {
                console.error('❌ Deploy failed:', result.error);
                process.exit(1);
            }
            break;
        }
        case 'status': {
            const result = await statusSkill();
            if (result.success) {
                console.log('✅ Get status successful!');
                console.log('📍 status:', result.status);
            }
            else {
                console.error('❌ Get status failed:', result.error);
                process.exit(1);
            }
            break;
        }
        case 'zip': {
            const targetPath = args[1] || (0, path_1.join)(process.cwd(), 'output.zip');
            const result = await zipSkill(targetPath, ignoreFilePath);
            if (result.success) {
                console.log('✅ Zip successful!');
                console.log('📍 status:', result.status);
            }
            else {
                console.error('❌ Zip failed:', result.error);
                process.exit(1);
            }
            break;
        }
        case 'test': {
            const result = await testSkill();
            if (result.success) {
                console.log('✅ Test successful!');
                console.log('📍 Message:', result.message);
            }
            else {
                console.error('❌ Test failed:', result.error);
                process.exit(1);
            }
            break;
        }
        default:
            console.error('Unknown command:', command);
            console.log('Available commands: status, deploy');
            process.exit(1);
    }
}
main().catch((error) => {
    console.error('Error:', error);
    process.exit(1);
});
//# sourceMappingURL=index.js.map