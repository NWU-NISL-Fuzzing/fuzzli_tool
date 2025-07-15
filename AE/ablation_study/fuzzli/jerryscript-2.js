for (var INDEX = 0; INDEX < 1000; INDEX++) {
    var NISLFuzzingFunc = function (fn) {
        var rootStack = '';
        try {
            throw new Error();
        } catch (error) {
            if (error.stack) {
                rootStack = error.stack.split('\n').slice(3).join('\n');
            }
        }
        return function (arg) {
        };
    };
}
var NISLParameter0 = function (data) {
};
var NISLCallingResult = NISLFuzzingFunc(NISLParameter0);
print(NISLCallingResult);