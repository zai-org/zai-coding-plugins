"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getDeployStatus = exports.uploadAndDeploy = exports.deployProject = exports.getUploadParamsForDeploy = void 0;
;
;
;
;
;
const urls = {
    getUploadParamsForDeploy: `/deployeo/client/getUploadParameters`,
    deployProject: '/deployeo/client/createDeployment',
    uploadAndDeploy: '/deployeo/client/uploadAndDeploy',
    getDeployStatus: '/deployeo/client/getDeployStatus'
};
const getUploadParamsForDeploy = async (projectId) => {
    // Placeholder implementation - replace with actual API call
    const url = process.env.API_BASE_URL + urls.getUploadParamsForDeploy;
    console.log(`getUploadParamsForDeploy url: ${url}, projectId=${projectId || ""}`);
    try {
        const response = await fetch(url + `?projectId=${projectId || ""}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.ANTHROPIC_AUTH_TOKEN || ""}`
            },
        });
        return handleHttpResponse(response);
    }
    catch (error) {
        // Fallback to placeholder values if API call fails
        console.error('Failed to get upload params:', error);
        throw error;
    }
};
exports.getUploadParamsForDeploy = getUploadParamsForDeploy;
const deployProject = async (arg) => {
    // Placeholder implementation - replace with actual API call
    const url = process.env.API_BASE_URL + urls.deployProject;
    console.log('deployProject url:', url);
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.ANTHROPIC_AUTH_TOKEN || ""}`
            },
            body: JSON.stringify(arg)
        });
        return handleHttpResponse(response);
    }
    catch (error) {
        console.error('Failed to deploy project:', error);
        throw error;
    }
};
exports.deployProject = deployProject;
const uploadAndDeploy = async (file, env, projectId) => {
    const url = process.env.API_BASE_URL + urls.uploadAndDeploy;
    console.info(`uploadAndDeploy url: ${url}, projectId=${projectId || ""}, file=${file.name}, env=${JSON.stringify(env)}`);
    try {
        var formdata = new FormData();
        formdata.append("file", file);
        if (projectId) {
            formdata.append("projectId", projectId);
        }
        env?.forEach(pair => {
            if (!!pair.key) {
                formdata.append("env", `${pair.key}=${pair.value}`);
            }
        });
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Connection': 'keep-alive',
                'Authorization': `Bearer ${process.env.ANTHROPIC_AUTH_TOKEN || ""}`
            },
            body: formdata
        });
        return handleHttpResponse(response);
    }
    catch (error) {
        console.error('Failed to upload and deploy:', error);
        throw error;
    }
};
exports.uploadAndDeploy = uploadAndDeploy;
const getDeployStatus = async (projectId, deploymentId) => {
    // Placeholder implementation - replace with actual API call
    const url = process.env.API_BASE_URL + urls.getDeployStatus;
    console.log(`getDeployStatus url: ${url}, projectId=${projectId || ""}, deploymentId=${deploymentId || ""}`);
    try {
        const response = await fetch(url + `?projectId=${projectId || ""}&deploymentId=${deploymentId || ""}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${process.env.ANTHROPIC_AUTH_TOKEN || ""}`
            },
        });
        return handleHttpResponse(response);
    }
    catch (error) {
        console.error('Failed to get deploy status:', error);
        throw error;
    }
};
exports.getDeployStatus = getDeployStatus;
const handleHttpResponse = async (response) => {
    const text = await response.text();
    console.debug(`API request result: (${response.status}): ${text}`);
    if (!response.ok) {
        throw new Error(`API request failed`);
    }
    const resp = JSON.parse(text);
    if (resp.code !== 200) {
        throw new Error(`API error: ${resp.msg || 'Unknown error'}`);
    }
    return resp.data;
};
//# sourceMappingURL=service.js.map