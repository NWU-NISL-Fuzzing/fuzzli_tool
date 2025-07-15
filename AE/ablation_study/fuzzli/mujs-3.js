var NISLFuzzingFunc = 
function(obj) {
    if (obj === null || typeof obj !== "object") return obj;
    if (obj instanceof Object) var copy = {
        __proto__: obj.__proto__
    };
    for (NISLi = 0; NISLi < 16 - 1; NISLi++) {
        copy['prop-' + NISLi] = 1;
    }
    copy['foo'] = 123;
    for (NISLi = 0; NISLi < 1e4; NISLi++) {
        void Object.propertyIsEnumerable();
    }
    //object method mutation else var copy = Object.create(null);
    Object.getOwnPropertyNames(obj).forEach(function(key) {
        Object.defineProperty(copy, key, Object.getOwnPropertyDescriptor(obj, key));
    });
    return copy;
}
;
var NISLParameter0 = [8100.22215350674231304, -312449.24335857008128026];
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0);
print(NISLCallingResult);