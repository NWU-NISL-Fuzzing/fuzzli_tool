var NISLFuzzingFunc = function () {
    var targetObj = {};
    var obj = {
        0: targetObj,
        1: 4294967297,
        length: 4294967297
    };
    return Array.prototype.lastIndexOf.call(obj, targetObj) === -1 && Array.prototype.lastIndexOf.call(obj, 3) === -1;
};
NISLFuzzingFunc();
