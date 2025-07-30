var __spreadArrays = (this && this.__spreadArrays) || function () {
    for (var s = 0, i = 0, il = arguments.length; i < il; i++) s += arguments[i].length;
    for (var r = Array(s), k = 0, i = 0; i < il; i++)
        for (var a = arguments[i], j = 0, jl = a.length; j < jl; j++, k++)
            r[k] = a[j];
    return r;
};
import { r as registerInstance, h, g as getElement } from './core-692256d4.js';
/**
 * Core platform service names
 */
var PlatformServiceName;
(function (PlatformServiceName) {
    PlatformServiceName["Translate"] = "translate";
    PlatformServiceName["Http"] = "http";
    PlatformServiceName["Route"] = "route";
    PlatformServiceName["Notification"] = "notifications";
    PlatformServiceName["Query"] = "query";
    PlatformServiceName["CommandBus"] = "commandBus";
    PlatformServiceName["Dialog"] = "dialog";
    PlatformServiceName["EventDispatcher"] = "eventDispatcher";
    PlatformServiceName["LimetypesState"] = "state.limetypes";
    PlatformServiceName["LimeobjectsState"] = "state.limeobjects";
    PlatformServiceName["ApplicationState"] = "state.application";
    PlatformServiceName["ConfigsState"] = "state.configs";
    PlatformServiceName["FiltersState"] = "state.filters";
    PlatformServiceName["DeviceState"] = "state.device";
    PlatformServiceName["TaskState"] = "state.tasks";
})(PlatformServiceName || (PlatformServiceName = {}));
var Operator;
(function (Operator) {
    Operator["AND"] = "AND";
    Operator["OR"] = "OR";
    Operator["EQUALS"] = "=";
    Operator["NOT"] = "!";
    Operator["GREATER"] = ">";
    Operator["LESS"] = "<";
    Operator["IN"] = "IN";
    Operator["BEGINS"] = "=?";
    Operator["LIKE"] = "?";
    Operator["LESS_OR_EQUAL"] = "<=";
    Operator["GREATER_OR_EQUAL"] = ">=";
})(Operator || (Operator = {}));
/**
 * Events dispatched by the commandbus event middleware
 */
var CommandEvent;
(function (CommandEvent) {
    /**
     * Dispatched when the command has been received by the commandbus.
     * Calling `preventDefault()` on the event will stop the command from being handled
     *
     * @detail { command }
     */
    CommandEvent["Received"] = "command.received";
    /**
     * Dispatched when the command has been handled by the commandbus
     *
     * @detail { command, result }
     */
    CommandEvent["Handled"] = "command.handled";
    /**
     * Dispatched if an error occurs while handling the command
     *
     * @detail { command, error }
     */
    CommandEvent["Failed"] = "command.failed";
})(CommandEvent || (CommandEvent = {}));
var TaskState;
(function (TaskState) {
    /**
     * Task state is unknown
     */
    TaskState["Pending"] = "PENDING";
    /**
     * Task was started by a worker
     */
    TaskState["Started"] = "STARTED";
    /**
     * Task is waiting for retry
     */
    TaskState["Retry"] = "RETRY";
    /**
     * Task succeeded
     */
    TaskState["Success"] = "SUCCESS";
    /**
     * Task failed
     */
    TaskState["Failure"] = "FAILURE";
})(TaskState || (TaskState = {}));
/**
 * Gets an object with all configs where key is used as key.
 *
 * @param {ConfigsOptions} options state decorator options
 *
 * @returns {Function} state decorator
 */
function Configs(options) {
    var config = {
        name: PlatformServiceName.ConfigsState,
    };
    return createStateDecorator(options, config);
}
/**
 * Get the limeobject for the current context
 *
 * @param {StateOptions} [options] state decorator options
 *
 * @returns {Function} state decorator
 */
function CurrentLimeobject(options) {
    if (options === void 0) { options = {}; }
    var config = {
        name: PlatformServiceName.LimeobjectsState,
    };
    options.map = __spreadArrays([currentLimeobject], (options.map || []));
    return createStateDecorator(options, config);
}
function currentLimeobject(limeobjects) {
    var _b = this.context, limetype = _b.limetype, id = _b.id; // tslint:disable-line:no-invalid-this
    if (!limeobjects[limetype]) {
        return undefined;
    }
    return limeobjects[limetype].find(function (object) { return object.id === id; });
}
/**
 * Get the application session
 *
 * @param {StateOptions} [options] state decorator options
 *
 * @returns {Function} state decorator
 */
function Session(options) {
    if (options === void 0) { options = {}; }
    var config = {
        name: PlatformServiceName.ApplicationState,
    };
    options.map = __spreadArrays([getSession], (options.map || []));
    return createStateDecorator(options, config);
}
function getSession(applicationData) {
    return applicationData.session;
}
/**
 * Create a new state decorator
 *
 * @param {StateOptions} options decorator options
 * @param {StateDecoratorConfig} config decorator configuration
 *
 * @returns {Function} state decorator
 */
function createStateDecorator(options, config) {
    return function (component, property) {
        var componentMapping = getComponentMapping(component, property, options, config);
        if (componentMapping.properties.length === 1) {
            extendLifecycleMethods(component, componentMapping.properties);
        }
    };
}
var componentMappings = [];
/**
 * Get mappings for a component, containing the properties with a state decorator for
 * the current component
 *
 * @param {Component} component the component class containing the decorator
 * @param {string} property name of the property
 * @param {StateOptions} options decorator options
 * @param {StateDecoratorConfig} config decorator configuration
 *
 * @returns {ComponentMapping} mappings for the component
 */
function getComponentMapping(component, property, options, config) {
    var mapping = componentMappings.find(function (item) { return item.component === component; });
    if (!mapping) {
        mapping = {
            properties: [],
            component: component,
        };
        componentMappings.push(mapping);
    }
    mapping.properties.push({
        options: options,
        name: property,
        service: {
            name: config.name,
            method: config.method || 'subscribe',
        },
    });
    return mapping;
}
/**
 * Extend the lifecycle methods on the component
 *
 * @param {Component} component the component to extend
 * @param {Property[]} properties the properties with which to extend the component
 *
 * @returns {void}
 */
function extendLifecycleMethods(component, properties) {
    var originalComponentWillLoad = component.componentWillLoad;
    var originalComponentDidUnload = component.componentDidUnload;
    var subscriptions = [];
    component.componentWillLoad = function () {
        var _this = this;
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        properties.forEach(function (property) {
            subscribe.apply(_this, [subscriptions, property]);
        });
        if (originalComponentWillLoad) {
            return originalComponentWillLoad.apply(this, args);
        }
    };
    component.componentDidUnload = function () {
        var args = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            args[_i] = arguments[_i];
        }
        if (originalComponentDidUnload) {
            originalComponentDidUnload.apply(this, args);
        }
        unsubscribeAll.apply(this, [subscriptions]);
    };
}
/**
 * Subscribe to changes from the state
 * Use as `subscription.apply(componentToAugment, [subscriptions, property])`.
 *
 * @param {Subscription[]} subscriptions existing subscriptions on the component
 * @param {Property} property property to update when subscription triggers
 *
 * @returns {void}
 */
function subscribe(subscriptions, property) {
    var _this = this;
    var subscription = subscriptions.find(function (item) { return item.instance === _this; });
    if (!subscription) {
        subscription = {
            instance: this,
            unsubscribes: [],
        };
        subscriptions.push(subscription);
    }
    var unsubscribe = createSubscription.apply(this, [
        property.options,
        property.name,
        property.service.name,
        property.service.method,
    ]);
    subscription.unsubscribes.push(unsubscribe);
}
/**
 * Unsubscribe to changes from the state
 *
 * @param {Subscription[]} subscriptions existing subscriptions on the component
 *
 * @returns {void}
 */
function unsubscribeAll(subscriptions) {
    var _this = this;
    if (subscriptions === void 0) { subscriptions = []; }
    var subscription = subscriptions.find(function (item) { return item.instance === _this; });
    subscription.unsubscribes.forEach(function (unsubscribe) { return unsubscribe(); });
    for (var i = subscriptions.length - 1; i >= 0; i--) {
        var item = subscriptions[i];
        if (item.instance !== this) {
            continue;
        }
        subscriptions.splice(i, 1);
    }
}
/**
 * Get a function that accepts a state, and updates the given property
 * on the given component with that state
 *
 * @param {any} instance the component to augment
 * @param {string} property name of the property on the component
 *
 * @returns {Function} updates the state
 */
function mapState(instance, property) {
    return function (state) {
        instance[property] = state;
    };
}
/**
 * Create a state subscription
 * Use as `createSubscription.apply(componentToAugment, [options, property, name, method])`.
 *
 * @param {StateOptions} options options for the selector
 * @param {string} property name of the property on the component
 * @param {string} name name of the state service
 * @param {string} method name of method on the state service
 *
 * @returns {Function} unsubscribe function
 */
function createSubscription(options, property, name, method) {
    var myOptions = Object.assign({}, options);
    bindFunctions(myOptions, this);
    var platform = this.platform;
    if (!platform.has(name)) {
        throw new Error("Service " + name + " does not exist");
    }
    var service = platform.get(name);
    return service[method](mapState(this, property), myOptions);
}
/**
 * Bind connect functions to the current scope
 *
 * @param {StateOptions} options options for the selector
 * @param {*} scope the current scope to bind to
 *
 * @returns {void}
 */
function bindFunctions(options, scope) {
    if (options.filter) {
        options.filter = options.filter.map(function (func) { return func.bind(scope); });
    }
    if (options.map) {
        options.map = options.map.map(function (func) { return func.bind(scope); });
    }
}
var __decorate = (undefined && undefined.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function")
        r = Reflect.decorate(decorators, target, key, desc);
    else
        for (var i = decorators.length - 1; i >= 0; i--)
            if (d = decorators[i])
                r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var Test = /** @class */ (function () {
    function Test(hostRef) {
        var _this = this;
        registerInstance(this, hostRef);
        this.document = {};
        this.session = {};
        this.config = {};
        this.testing = true;
        this.testing3 = "test";
        this.includePerson = true;
        this.includeCoworker = true;
        this.cloneDocument = true;
        this.isOpen = false;
        this.allowedExtensions = Object.freeze(["PDF", "DOC", "DOCX"]);
        this.setCloneDocument = function (event) {
            event.stopPropagation();
            _this.cloneDocument = event.detail;
        };
        this.openDialog = function () {
            _this.isOpen = true;
        };
        this.closeDialog = function () {
            _this.isOpen = false;
        };
    }
    Test.prototype.goToScrive = function (id, scriveDocId) {
        var host = this.config.limepkg_scrive.scriveHost;
        var lang = this.session.language;
        window.open(host + "/public/?limeDocId=" + id + "&lang=" + lang + "&usePerson=" + this.includePerson + "&useCoworker=" + this.includeCoworker + "&cloneDocument=" + this.cloneDocument + "&scriveDocId=" + scriveDocId);
    };
    Test.prototype.files = function () {
        var _a;
        var fileMap = ((_a = this.document) === null || _a === void 0 ? void 0 : _a._files) || {};
        var fileIds = Object.keys(fileMap);
        return fileIds.map(function (id) { return fileMap[id]; });
    };
    Test.prototype.isSignable = function (file) {
        return this.allowedExtensions.includes((file.extension || "").toUpperCase());
    };
    Test.prototype.render = function () {
        var _this = this;
        console.log("---------", this);
        if (this.context.limetype !== 'document') {
            return;
        }
        var signableFiles = this.files().filter(this.isSignable, this);
        var noSignableFiles = signableFiles.length === 0;
        var tooManySignableFiles = signableFiles.length > 1;
        if (noSignableFiles || tooManySignableFiles) {
            return;
        }
        var translate = this.platform.get(PlatformServiceName.Translate);
        var esignLabel = translate.get("limepkg_scrive.primary_action");
        var cloneLabel = translate.get("limepkg_scrive.clone_document");
        var cloneHintLabel = translate.get("limepkg_scrive.clone_hint");
        var cloneInfoLabel = translate.get("limepkg_scrive.clone_info");
        var okLabel = translate.get("limepkg_scrive.ok");
        return (h("section", null, h("limel-button", { id: "scrive_esign_button", label: esignLabel, outlined: true, icon: "signature", onClick: function () { var _a; return _this.goToScrive(_this.context.id, (_a = _this.document) === null || _a === void 0 ? void 0 : _a.scrive_document_id); } }), h("hr", null), h("p", null, h("h1", null, "hello world")), h("hr", null), h("p", null, h("limel-flex-container", { justify: "start" }, h("limel-checkbox", { label: cloneLabel, checked: this.cloneDocument, onChange: this.setCloneDocument }), h("limel-icon-button", { icon: "question_mark", label: cloneHintLabel, onClick: this.openDialog }))), h("limel-dialog", { open: this.isOpen, onClose: this.closeDialog }, h("p", null, cloneInfoLabel), h("limel-button", { label: okLabel, onClick: this.closeDialog, slot: "button" }))));
    };
    Object.defineProperty(Test.prototype, "element", {
        get: function () { return getElement(this); },
        enumerable: true,
        configurable: true
    });
    Object.defineProperty(Test, "style", {
        get: function () { return ".container{margin-left:1.25rem;margin-right:1.25rem}#scrive_esign_button{isolation:isolate;position:relative}#scrive_esign_button:after{content:\"\";display:block;width:1.5rem;height:1.5rem;position:absolute;z-index:1;top:0;left:.25rem;bottom:0;margin:auto;background-image:url(\"data:image/svg+xml; utf8, <svg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 128.9 116.04\'><defs><style>.cls-1{fill:none;}.cls-2{fill:%2327282d;}</style></defs><g id=\'Layer_2\' data-name=\'Layer 2\'><g id=\'S_Mark_Dark\' data-name=\'S Mark Dark\'><g id=\'S_Black\' data-name=\'S Black\'><rect class=\'cls-1\' width=\'128.9\' height=\'116.04\'/><path class=\'cls-2\' d=\'M65.51,65.48a29.87,29.87,0,0,1,7.76,2,7.3,7.3,0,0,1,3.62,3,8.64,8.64,0,0,1,1,4.35A10.34,10.34,0,0,1,76,80.71a12.35,12.35,0,0,1-4.64,3.53c-4.65,2.1-11.05,2.69-16.06,2.73A40.35,40.35,0,0,1,44,85.53,20.24,20.24,0,0,1,36.8,82,13.63,13.63,0,0,1,33,77.1,13.1,13.1,0,0,1,31.86,72H17.67A28.57,28.57,0,0,0,20.6,83a22,22,0,0,0,6.22,7.55,31.48,31.48,0,0,0,8.63,4.6,48.07,48.07,0,0,0,9.91,2.31,75.66,75.66,0,0,0,10.35.63c10.94,0,25-2.14,32.12-11.44A22.22,22.22,0,0,0,92.07,73.2a18,18,0,0,0-1.61-7.8A19.6,19.6,0,0,0,86,59.48a22.44,22.44,0,0,0-6.43-4,29.84,29.84,0,0,0-7.69-2.1C63.47,52.2,44.59,50.46,39.22,48A7.21,7.21,0,0,1,35.56,45a7.69,7.69,0,0,1-1-4.3,8.74,8.74,0,0,1,1.72-5.52,12.69,12.69,0,0,1,4.6-3.53,26.67,26.67,0,0,1,6.37-1.85,43.93,43.93,0,0,1,6.88-.55,34.38,34.38,0,0,1,12.25,2,17.4,17.4,0,0,1,7.35,5,11.88,11.88,0,0,1,2.67,7H90.64A27.58,27.58,0,0,0,87.9,33.17a24.4,24.4,0,0,0-6.73-8,31.92,31.92,0,0,0-11-5.19,60.15,60.15,0,0,0-15.84-1.92A52.27,52.27,0,0,0,36.22,21a25.4,25.4,0,0,0-11.67,8.24,20.92,20.92,0,0,0-4.17,13A18.17,18.17,0,0,0,26.49,56,22.45,22.45,0,0,0,32.92,60a29.63,29.63,0,0,0,7.61,2.06C48.91,63.23,57.21,64.37,65.51,65.48Z\'/><path class=\'cls-2\' d=\'M111.23,89.19a8.84,8.84,0,1,1-8.84-8.88A8.87,8.87,0,0,1,111.23,89.19Z\'/></g></g></g></svg>\");background-color:var(--lime-elevated-surface-background-color);background-size:contain;background-repeat:no-repeat;background-position:50%}"; },
        enumerable: true,
        configurable: true
    });
    return Test;
}());
__decorate([
    CurrentLimeobject()
], Test.prototype, "document", void 0);
__decorate([
    Session()
], Test.prototype, "session", void 0);
__decorate([
    Configs({})
], Test.prototype, "config", void 0);
export { Test as lwc_limepkg_scrive };
