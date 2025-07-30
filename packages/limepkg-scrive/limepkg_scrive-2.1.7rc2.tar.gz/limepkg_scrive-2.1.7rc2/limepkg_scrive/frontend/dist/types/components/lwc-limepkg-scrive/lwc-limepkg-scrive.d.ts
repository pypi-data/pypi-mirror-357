import { LimeWebComponent, LimeWebComponentContext, LimeWebComponentPlatform } from '@limetech/lime-web-components-interfaces';
export declare class Test implements LimeWebComponent {
    private document;
    private session;
    platform: LimeWebComponentPlatform;
    private config;
    context: LimeWebComponentContext;
    element: HTMLElement;
    testing: boolean;
    testing2: any;
    testing3: string;
    includePerson: boolean;
    includeCoworker: boolean;
    private cloneDocument;
    private isOpen;
    private goToScrive;
    private files;
    private allowedExtensions;
    private isSignable;
    private setCloneDocument;
    private openDialog;
    private closeDialog;
    render(): any;
}
