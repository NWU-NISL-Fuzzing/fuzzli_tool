for (var INDEX = 0; INDEX < 1000; INDEX++) {
    var NISLFuzzingFunc = function () {
        var a = true;
        eval('var a = false');
        return a;
    };
}
var NISLCallingResult = NISLFuzzingFunc();
print(NISLCallingResult);