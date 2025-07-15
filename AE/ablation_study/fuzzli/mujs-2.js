var NISLFuzzingFunc = 
function() {
    var obj = {};
    var attr = {
        writable: true
    };
    for (NISLi = 0; NISLi < 16 - 1; NISLi++) {
        obj['prop-' + NISLi] = 1;
    }
    obj['foo'] = 123;
    for (NISLi = 0; NISLi < 1e4; NISLi++) {
        void Object.preventExtensions(obj);
    }
    //object method mutation
    Object.defineProperty(obj, "property", attr);
    return obj.hasOwnProperty("property") && typeof obj.property === "undefined";
}
;
var NISLCallingResult = NISLFuzzingFunc();
print(NISLCallingResult);