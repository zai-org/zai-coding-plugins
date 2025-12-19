export interface KeyValuePair {
    key: string;
    value: string;
}
export interface UploadParams {
    secretId: string;
    secretKey: string;
    token: string;
    bucket: string;
    region: string;
    targetPath: string;
    type: string;
}
export interface CreateDeploymentArg {
    projectId?: string;
    targetPath: string;
    env: KeyValuePair[];
}
export interface CreateDeploymentResult {
    projectId: string;
    deploymentId: string;
}
export interface GetDeploymentStatusResult {
    id: string;
    status: string;
    startTime?: string;
    endTime?: string;
    result?: {
        message?: string;
        previewUrl?: string;
        coverUrl?: string;
    };
}
export declare const getUploadParamsForDeploy: (projectId?: string) => Promise<UploadParams>;
export declare const deployProject: (arg: CreateDeploymentArg) => Promise<CreateDeploymentResult>;
export declare const uploadAndDeploy: (file: File, env: KeyValuePair[], projectId?: string) => Promise<CreateDeploymentResult>;
export declare const getDeployStatus: (projectId: string, deploymentId: string) => Promise<GetDeploymentStatusResult>;
//# sourceMappingURL=service.d.ts.map